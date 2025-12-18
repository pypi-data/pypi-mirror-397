#include "magneto.h"
#include <string.h>
#include <ctype.h>

/* ============================================================================
 * FONCTIONS STATIQUES INTERNES (NON EXPORTÉES)
 * ============================================================================ */

/* Vérifie si la position donnée est une frontière de mot pour l'option WHOLE_WORD */
static MAGNETO_INLINE int is_word_char(uint8_t ch) {
    // Caractères considérés comme faisant partie d'un mot (alphanumérique + underscore)
    return isalnum(ch) || ch == '_';
}

static int magneto_is_boundary(const char *data, size_t pos, size_t size)
{
    // Vérification du caractère PRÉCÉDENT
    if (pos > 0) {
        if (is_word_char((uint8_t)data[pos - 1])) {
            return 0; // Le caractère précédent fait partie d'un mot
        }
    }
    
    // Vérification du caractère SUIVANT (la position `pos` est le début du match)
    if (pos < size) {
        if (is_word_char((uint8_t)data[pos])) {
            return 0; // Le caractère suivant fait partie d'un mot
        }
    }
    
    return 1; // C'est une limite de mot ou début/fin de buffer
}

/* ============================================================================
 * IMPLÉMENTATION DE L'API PUBLIQUE
 * ============================================================================ */

/**
 * @brief Compile un motif. **Logique Case-Insensitive corrigée.**
 */
MagnetoResult magneto_compile(
    MagnetoPattern *MAGNETO_RESTRICT p,
    const char *MAGNETO_RESTRICT pattern,
    uint8_t options)
{
    /* Validation des paramètres */
    if (MAGNETO_UNLIKELY(p == NULL || pattern == NULL)) {
        return MAGNETO_ERR_NULL_PTR;
    }
    
    if (MAGNETO_UNLIKELY((options & ~(MAGNETO_OPTION_CASE_INSENSITIVE | MAGNETO_OPTION_WHOLE_WORD)) != 0)) {
        return MAGNETO_ERR_INVALID_OPTIONS;
    }
    
    /* Calcul de la longueur du motif (max MAGNETO_MAX_PATTERN) */
    size_t len = strnlen(pattern, MAGNETO_MAX_PATTERN + 1);

    if (MAGNETO_UNLIKELY(len == 0)) {
        return MAGNETO_ERR_PATTERN_EMPTY;
    }
    if (MAGNETO_UNLIKELY(len > MAGNETO_MAX_PATTERN)) {
        return MAGNETO_ERR_PATTERN_TOO_LONG;
    }
    
    /* Initialisation de la structure */
    memset(p, 0, sizeof(MagnetoPattern));
    p->length = (uint8_t)len;
    p->match_bit = 1ULL << (len - 1);
    p->options = options;
    
    const uint8_t is_case_insensitive = options & MAGNETO_OPTION_CASE_INSENSITIVE;

    /* Pré-calcul des masques de caractères */
    for (size_t i = 0; i < len; i++) {
        uint8_t ch = (uint8_t)pattern[i];
        
        // 1. Sensible à la casse (toujours appliqué)
        p->masks[ch] |= (1ULL << i);
        
        // 2. Insensible à la casse (Correction de la logique)
        if (is_case_insensitive) {
            if (isalpha(ch)) {
                uint8_t opposite = isupper(ch) ? (uint8_t)tolower(ch) : (uint8_t)toupper(ch);
                
                // Mappe le caractère opposé au même bit de position
                p->masks[opposite] |= (1ULL << i);
            }
        }
    }
    
    return MAGNETO_OK;
}

/**
 * @brief Version simplifiée sans options (compatibilité ascendante).
 */
MagnetoResult magneto_compile_simple(
    MagnetoPattern *MAGNETO_RESTRICT p,
    const char *MAGNETO_RESTRICT pattern)
{
    return magneto_compile(p, pattern, MAGNETO_OPTION_NONE);
}

/**
 * @brief Cœur de scan ultra-optimisé (Bitap + Unrolling)
 * Intègre la logique WHOLE_WORD
 */
static size_t magneto_scan_core(
    const MagnetoPattern *MAGNETO_RESTRICT p,
    const char *MAGNETO_RESTRICT data,
    size_t size,
    uint64_t *MAGNETO_RESTRICT state,
    size_t *MAGNETO_RESTRICT matches,
    size_t max_matches,
    int store_matches)
{
    if (MAGNETO_UNLIKELY(p == NULL || data == NULL || state == NULL)) {
        return 0;
    }
    
    uint64_t current_state = *state;
    const uint64_t match_bit = p->match_bit;
    const uint64_t *masks = p->masks;
    const size_t pattern_len = p->length;
    const uint8_t check_whole_word = p->options & MAGNETO_OPTION_WHOLE_WORD;
    size_t count = 0;
    
    /* Constante de décalage pré-calculée */
    const uint64_t shift_in = 1ULL;
    
    /* Déroulement de boucle agressif : 8 octets à la fois */
    size_t i = 0;
    const size_t unroll_count = 8;
    const size_t fast_size = size - (size % unroll_count); // S'assurer que le reste est traité séparément

    for (; MAGNETO_LIKELY(i < fast_size); i += unroll_count) {
        
        /* Traitement de 8 octets sans branchement interne pour maximiser le pipeline */
        uint64_t state0 = ((current_state << 1) | shift_in) & masks[(uint8_t)data[i]];
        uint64_t state1 = ((state0 << 1) | shift_in) & masks[(uint8_t)data[i + 1]];
        uint64_t state2 = ((state1 << 1) | shift_in) & masks[(uint8_t)data[i + 2]];
        uint64_t state3 = ((state2 << 1) | shift_in) & masks[(uint8_t)data[i + 3]];
        uint64_t state4 = ((state3 << 1) | shift_in) & masks[(uint8_t)data[i + 4]];
        uint64_t state5 = ((state4 << 1) | shift_in) & masks[(uint8_t)data[i + 5]];
        uint64_t state6 = ((state5 << 1) | shift_in) & masks[(uint8_t)data[i + 6]];
        current_state = ((state6 << 1) | shift_in) & masks[(uint8_t)data[i + 7]];
        
        /* Vérification groupée des matches (optimisation du branch prediction) */
        if (MAGNETO_UNLIKELY(state0 & match_bit)) {
            size_t match_pos = i - pattern_len + 1;
            if (!check_whole_word || magneto_is_boundary(data, match_pos, size) && magneto_is_boundary(data, match_pos + pattern_len, size)) {
                if (store_matches && count < max_matches) matches[count] = match_pos;
                count++;
            }
        }
        if (MAGNETO_UNLIKELY(state1 & match_bit)) {
            size_t match_pos = i + 1 - pattern_len + 1;
            if (!check_whole_word || magneto_is_boundary(data, match_pos, size) && magneto_is_boundary(data, match_pos + pattern_len, size)) {
                if (store_matches && count < max_matches) matches[count] = match_pos;
                count++;
            }
        }
        if (MAGNETO_UNLIKELY(state2 & match_bit)) {
            size_t match_pos = i + 2 - pattern_len + 1;
            if (!check_whole_word || magneto_is_boundary(data, match_pos, size) && magneto_is_boundary(data, match_pos + pattern_len, size)) {
                if (store_matches && count < max_matches) matches[count] = match_pos;
                count++;
            }
        }
        if (MAGNETO_UNLIKELY(state3 & match_bit)) {
            size_t match_pos = i + 3 - pattern_len + 1;
            if (!check_whole_word || magneto_is_boundary(data, match_pos, size) && magneto_is_boundary(data, match_pos + pattern_len, size)) {
                if (store_matches && count < max_matches) matches[count] = match_pos;
                count++;
            }
        }
        if (MAGNETO_UNLIKELY(state4 & match_bit)) {
            size_t match_pos = i + 4 - pattern_len + 1;
            if (!check_whole_word || magneto_is_boundary(data, match_pos, size) && magneto_is_boundary(data, match_pos + pattern_len, size)) {
                if (store_matches && count < max_matches) matches[count] = match_pos;
                count++;
            }
        }
        if (MAGNETO_UNLIKELY(state5 & match_bit)) {
            size_t match_pos = i + 5 - pattern_len + 1;
            if (!check_whole_word || magneto_is_boundary(data, match_pos, size) && magneto_is_boundary(data, match_pos + pattern_len, size)) {
                if (store_matches && count < max_matches) matches[count] = match_pos;
                count++;
            }
        }
        if (MAGNETO_UNLIKELY(state6 & match_bit)) {
            size_t match_pos = i + 6 - pattern_len + 1;
            if (!check_whole_word || magneto_is_boundary(data, match_pos, size) && magneto_is_boundary(data, match_pos + pattern_len, size)) {
                if (store_matches && count < max_matches) matches[count] = match_pos;
                count++;
            }
        }
        if (MAGNETO_UNLIKELY(current_state & match_bit)) {
            size_t match_pos = i + 7 - pattern_len + 1;
            if (!check_whole_word || magneto_is_boundary(data, match_pos, size) && magneto_is_boundary(data, match_pos + pattern_len, size)) {
                if (store_matches && count < max_matches) matches[count] = match_pos;
                count++;
            }
        }
    }
    
    /* Traiter les octets restants (si size n'est pas un multiple de 8) */
    for (; i < size; i++) {
        current_state = ((current_state << 1) | shift_in) & masks[(uint8_t)data[i]];
        
        if (MAGNETO_UNLIKELY(current_state & match_bit)) {
            size_t match_pos = i - pattern_len + 1;

            if (!check_whole_word || magneto_is_boundary(data, match_pos, size) && magneto_is_boundary(data, match_pos + pattern_len, size)) {
                if (store_matches && count < max_matches) {
                    matches[count] = match_pos;
                }
                count++;
            }
        }
    }
    
    *state = current_state;
    return count;
}


/**
 * @brief Scanne un buffer mémoire et stocke les positions de match.
 */
size_t magneto_scan(
    const MagnetoPattern *MAGNETO_RESTRICT p,
    const char *MAGNETO_RESTRICT data,
    size_t size,
    uint64_t *MAGNETO_RESTRICT state,
    size_t *MAGNETO_RESTRICT matches,
    size_t max_matches)
{
    /* Si matches est NULL ou max_matches est 0, c'est un simple comptage */
    if (MAGNETO_UNLIKELY(matches == NULL || max_matches == 0)) {
        return magneto_scan_core(p, data, size, state, NULL, 0, 0);
    }
    
    return magneto_scan_core(p, data, size, state, matches, max_matches, 1);
}

/**
 * @brief Recherche la première occurrence seulement (la plus rapide).
 */
size_t magneto_find_first(
    const MagnetoPattern *MAGNETO_RESTRICT p,
    const char *MAGNETO_RESTRICT data,
    size_t size,
    uint64_t *MAGNETO_RESTRICT state)
{
    if (MAGNETO_UNLIKELY(p == NULL || data == NULL || state == NULL)) {
        return SIZE_MAX;
    }
    
    uint64_t current_state = *state;
    const uint64_t match_bit = p->match_bit;
    const uint64_t *masks = p->masks;
    const size_t pattern_len = p->length;
    const uint64_t shift_in = 1ULL;
    const uint8_t check_whole_word = p->options & MAGNETO_OPTION_WHOLE_WORD;
    
    /* Pas de déroulement de boucle ici, car l'arrêt est imprévisible (trouver le premier) */
    for (size_t i = 0; i < size; i++) {
        current_state = ((current_state << 1) | shift_in) & masks[(uint8_t)data[i]];
        
        if (MAGNETO_UNLIKELY(current_state & match_bit)) {
            size_t match_pos = i - pattern_len + 1;
            
            if (!check_whole_word || magneto_is_boundary(data, match_pos, size) && magneto_is_boundary(data, match_pos + pattern_len, size)) {
                
                *state = current_state;
                return match_pos;
            }
        }
    }
    
    *state = current_state;
    return SIZE_MAX;
}

/**
 * @brief Compte le nombre d'occurrences.
 */
size_t magneto_count(
    const MagnetoPattern *MAGNETO_RESTRICT p,
    const char *MAGNETO_RESTRICT data,
    size_t size,
    uint64_t *MAGNETO_RESTRICT state)
{
    /* Utiliser la version core avec store_matches = 0 (mode comptage) */
    return magneto_scan_core(p, data, size, state, NULL, 0, 0);
}

/**
 * @brief Fonctions d'utilité
 */
uint32_t magneto_version(void)
{
    return MAGNETO_VERSION;
}

size_t magneto_pattern_size(void)
{
    return sizeof(MagnetoPattern);
}