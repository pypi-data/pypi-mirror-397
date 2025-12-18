#ifndef MAGNETO_H
#define MAGNETO_H

#include <stdint.h>
#include <stddef.h>

/* ============================================================================
 * DÉTECTION DU COMPILATEUR & ATTRIBUTS DE PERFORMANCE
 * ============================================================================ */
#if defined(_MSC_VER)
    #define MAGNETO_ALIGNED(x) __declspec(align(x))
    #define MAGNETO_RESTRICT    __restrict
    #define MAGNETO_INLINE      __forceinline
    #define MAGNETO_LIKELY(x)   (x)
    #define MAGNETO_UNLIKELY(x) (x)
#elif defined(__GNUC__) || defined(__clang__)
    #define MAGNETO_ALIGNED(x)  __attribute__((aligned(x)))
    #define MAGNETO_RESTRICT    __restrict__
    #define MAGNETO_INLINE      __attribute__((always_inline)) inline
    #define MAGNETO_LIKELY(x)   __builtin_expect(!!(x), 1)
    #define MAGNETO_UNLIKELY(x) __builtin_expect(!!(x), 0)
#else
    #define MAGNETO_ALIGNED(x)
    #define MAGNETO_RESTRICT
    #define MAGNETO_INLINE      inline
    #define MAGNETO_LIKELY(x)   (x)
    #define MAGNETO_UNLIKELY(x) (x)
#endif

/* ============================================================================
 * CONSTANTES DE CONFIGURATION
 * ============================================================================ */
/* 
 * MAX_PATTERN = 64 car nous utilisons des registres 64-bit natifs.
 * C'est le cœur de l'algorithme Bitap/Shift-AND : 1 opération CPU = 64 comparaisons.
 */
#define MAGNETO_MAX_PATTERN             64

/* 
 * Version sémantique du moteur (Major.Minor.Patch).
 * Permet aux utilisateurs de vérifier la compatibilité ABI/API.
 */
#define MAGNETO_VERSION_MAJOR           1
#define MAGNETO_VERSION_MINOR           0
#define MAGNETO_VERSION_PATCH           0
#define MAGNETO_VERSION                 ((MAGNETO_VERSION_MAJOR << 16) | \
                                         (MAGNETO_VERSION_MINOR << 8) | \
                                         (MAGNETO_VERSION_PATCH))

/*
 * Options de compilation pour fine-tuning.
 * Peuvent être activées via des flags de compilation (-DMAGNETO_USE_POPCOUNT).
 */
#define MAGNETO_OPTION_NONE             0x00
#define MAGNETO_OPTION_CASE_INSENSITIVE 0x01  /* Recherche insensible à la casse */
#define MAGNETO_OPTION_WHOLE_WORD       0x02  /* Recherche de mots entiers */

/* ============================================================================
 * TYPES ET STRUCTURES
 * ============================================================================ */
typedef enum {
    MAGNETO_OK = 0,
    MAGNETO_ERR_PATTERN_TOO_LONG   = -1,
    MAGNETO_ERR_PATTERN_EMPTY      = -2,
    MAGNETO_ERR_NULL_PTR           = -3,
    MAGNETO_ERR_INVALID_OPTIONS    = -4,
    MAGNETO_ERR_BUFFER_TOO_SMALL   = -5,
    MAGNETO_ERR_INTERNAL           = -99
} MagnetoResult;

/* 
 * Structure d'un pattern compilé.
 * Alignée sur 64 octets (Cache Line) pour éviter les False Sharing
 * et optimiser les accès mémoire.
 */
typedef struct MAGNETO_ALIGNED(64) {
    /* 
     * Table de lookup ASCII (256 entrées).
     * Chaque masque indique les positions dans le motif où le caractère apparaît.
     * Exemple: Si 'A' apparaît aux positions 1 et 3, alors masks['A'] = ...1010b
     */
    uint64_t masks[256];
    
    /*
     * Bit de succès (MSB du motif).
     * Quand l'état de recherche atteint ce bit, on a une correspondance.
     */
    uint64_t match_bit;
    
    /* Longueur réelle du motif (1..64) */
    uint8_t length;
    
    /* Options de recherche activées (case-insensitive, whole-word, etc.) */
    uint8_t options;
    
    /* Padding pour aligner la structure sur 64 octets */
    uint8_t _reserved[14];
} MagnetoPattern;

/* ============================================================================
 * API PUBLIQUE
 * ============================================================================ */
#ifdef __cplusplus
extern "C" {
#endif

/**
 * @brief Compile un motif pour une recherche ultra-rapide (pré-calcul des masques).
 * 
 * @param p        Pointeur vers la structure MagnetoPattern à initialiser.
 * @param pattern  Chaîne à chercher (ASCII, non NULL, max 64 caractères).
 * @param options  Options de recherche (MAGNETO_OPTION_*).
 * 
 * @return MAGNETO_OK en cas de succès, code d'erreur sinon.
 * 
 * @note Complexité: O(256 + n) où n = strlen(pattern)
 * @note Thread-safe si `p` est local à chaque thread.
 */
MagnetoResult magneto_compile(
    MagnetoPattern *MAGNETO_RESTRICT p,
    const char *MAGNETO_RESTRICT pattern,
    uint8_t options
);

/**
 * @brief Version simplifiée sans options (compatibilité ascendante).
 */
MagnetoResult magneto_compile_simple(
    MagnetoPattern *MAGNETO_RESTRICT p,
    const char *MAGNETO_RESTRICT pattern
);

/**
 * @brief Scanne un buffer mémoire avec un motif pré-compilé.
 * 
 * @param p             Pattern compilé (via magneto_compile).
 * @param data          Buffer de données à analyser.
 * @param size          Taille du buffer en octets.
 * @param state         État de la recherche (pour streaming).
 *                      Initialiser à 0 pour une nouvelle recherche.
 *                      Permet de trouver des motifs coupés entre buffers.
 * @param matches       Tableau de sortie pour stocker les positions des matches.
 * @param max_matches   Capacité du tableau `matches`.
 * 
 * @return Nombre de correspondances trouvées dans ce chunk.
 *         Si égal à `max_matches`, il peut y avoir plus de matches non reportés.
 * 
 * @note Complexité: O(n) où n = size, avec très faible constante.
 * @note Performance: ~1-2 cycles/octet sur CPU moderne.
 * @note Thread-safe: Oui, si chaque thread a son propre `state`.
 */
size_t magneto_scan(
    const MagnetoPattern *MAGNETO_RESTRICT p,
    const char *MAGNETO_RESTRICT data,
    size_t size,
    uint64_t *MAGNETO_RESTRICT state,
    size_t *MAGNETO_RESTRICT matches,
    size_t max_matches
);

/**
 * @brief Version optimisée pour la recherche de la première occurrence.
 * 
 * @param p        Pattern compilé.
 * @param data     Buffer de données.
 * @param size     Taille du buffer.
 * @param state    État de la recherche (comme magneto_scan).
 * 
 * @return Position de la première occurrence, ou SIZE_MAX si non trouvée.
 *         Si SIZE_MAX est retourné, `state` peut être réutilisé pour continuer.
 */
size_t magneto_find_first(
    const MagnetoPattern *MAGNETO_RESTRICT p,
    const char *MAGNETO_RESTRICT data,
    size_t size,
    uint64_t *MAGNETO_RESTRICT state
);

/**
 * @brief Version optimisée pour le comptage seulement (sans stockage des positions).
 * 
 * @param p        Pattern compilé.
 * @param data     Buffer de données.
 * @param size     Taille du buffer.
 * @param state    État de la recherche.
 * 
 * @return Nombre total d'occurrences dans le buffer.
 */
size_t magneto_count(
    const MagnetoPattern *MAGNETO_RESTRICT p,
    const char *MAGNETO_RESTRICT data,
    size_t size,
    uint64_t *MAGNETO_RESTRICT state
);

/**
 * @brief Récupère la version actuelle de Magneto.
 * 
 * @return Version encodée (voir MAGNETO_VERSION).
 */
uint32_t magneto_version(void);

/**
 * @brief Calcule la taille mémoire nécessaire pour un pattern.
 * 
 * @return Taille en octets de MagnetoPattern.
 */
size_t magneto_pattern_size(void);

#ifdef __cplusplus
}
#endif

/* ============================================================================
 * MACROS UTILITAIRES
 * ============================================================================ */
/**
 * @brief Macro pour initialiser un pattern sur la pile.
 * 
 * Usage:
 *     MAGNETO_PATTERN_INIT(my_pattern, "ERROR");
 */
#define MAGNETO_PATTERN_INIT(name, pattern_str) \
    MAGNETO_ALIGNED(64) MagnetoPattern name; \
    magneto_compile_simple(&name, pattern_str)

#endif /* MAGNETO_H */