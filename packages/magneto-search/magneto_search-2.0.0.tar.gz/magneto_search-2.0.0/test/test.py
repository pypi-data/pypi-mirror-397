import magneto
import os
import random
import time

# =========================================================================
# 0. PARAMÈTRES DU TEST
# =========================================================================

BIG_DATA_SIZE = 50 * 1024 * 1024   # 50 Mo pour un test de vitesse plus significatif
BLOCK_SIZE = 1024 * 1024           # 1 Mo par bloc
FILE_PATH = "magneto_test_data.bin"

# Scénarios de test complexes
SCENARIOS = [
    {
        "name": "Base Case: Simple et Rapide",
        "pattern": "Error",
        "options": magneto.OPTION_NONE,
        "insert_interval_ratio": 0.5, # Tous les 50% du bloc
        "case_variations": ["Error"],
        "expected_mode": "COUNT"
    },
    {
        "name": "Cas 1: Insensible à la Casse + Chevauchement",
        "pattern": "SECRET",
        "options": magneto.OPTION_CASE_INSENSITIVE,
        "insert_interval_ratio": 0.95, # Force le chevauchement avec une haute probabilité
        "case_variations": ["secret", "SECRET", "Secret"],
        "expected_mode": "STREAMING"
    },
    {
        "name": "Cas 2: Mot Entier + Casse Mixte",
        "pattern": "Warning",
        "options": magneto.OPTION_CASE_INSENSITIVE | magneto.OPTION_WHOLE_WORD,
        "insert_interval_ratio": 0.7,
        "case_variations": ["warning", "WARNING", "Warning"],
        "expected_mode": "WHOLE_WORD"
    },
    {
        "name": "Cas 3: Limite Bitap (64 Caractères)",
        "pattern": "A" * 60 + "ZZZZ", # 64 caractères max
        "options": magneto.OPTION_NONE,
        "insert_interval_ratio": 0.3,
        "case_variations": ["A" * 60 + "ZZZZ"],
        "expected_mode": "LIMIT"
    }
]

# =========================================================================
# FONCTION DE CRÉATION DU FICHIER (Optimisée)
# =========================================================================

# =========================================================================
# FONCTION DE CRÉATION DU FICHIER (CORRIGÉE)
# =========================================================================

def create_test_file(pattern, ratio, variations):
    """Crée le fichier de données avec insertion de motifs aléatoires."""
    
    if len(pattern) > 64:
        raise ValueError("Le motif est trop long pour Bitap (max 64)")
    
    PATTERN_BYTES_LIST = [v.encode('ascii') for v in variations]
    PATTERN_LEN = len(pattern)
    
    INSERT_INTERVAL = int(BLOCK_SIZE * ratio) 
    
    FILLER_BLOCK = b'a' * (INSERT_INTERVAL - PATTERN_LEN) 
    
    num_insertions = int(BIG_DATA_SIZE / INSERT_INTERVAL)
    total_expected_matches = 0
    
    # Nouvelle variable pour stocker la taille
    final_size = 0 
    
    print(f"\n[Fichier] Création de {BIG_DATA_SIZE / 1024 / 1024:.0f} Mo, {num_insertions} insertions attendues...")

    with open(FILE_PATH, 'wb') as f:
        for i in range(num_insertions):
            # 1. Écrit le remplissage
            f.write(FILLER_BLOCK)

            # 2. Écrit un motif choisi aléatoirement pour tester la casse
            match_to_write = random.choice(PATTERN_BYTES_LIST)
            f.write(match_to_write)
            total_expected_matches += 1

            # Pour le test WHOLE_WORD, nous ajoutons un suffixe sans espace
            if SCENARIOS[current_scenario_index]["options"] & magneto.OPTION_WHOLE_WORD:
                 f.write(b'X')
            
            if f.tell() >= BIG_DATA_SIZE:
                break
        
        # <<< C'EST LA CORRECTION >>>
        # Capturez la taille du fichier avant que le bloc 'with' ne se termine.
        final_size = f.tell() 
        
    # La variable 'f' est maintenant fermée ici.
    
    # Retournez la taille capturée.
    return total_expected_matches, final_size

# =========================================================================
# FONCTION DE TEST PRINCIPALE
# =========================================================================

def run_test(scenario, index):
    global current_scenario_index
    current_scenario_index = index
    
    print(f"\n{'='*60}\nTEST SCÉNARIO {index+1}: {scenario['name']}\n{'='*60}")
    
    # --- 1. Préparation des données ---
    start_time = time.time()
    expected_matches, final_file_size = create_test_file(
        scenario["pattern"], 
        scenario["insert_interval_ratio"], 
        scenario["case_variations"]
    )
    creation_time = time.time() - start_time
    print(f"[Timing] Création du fichier: {creation_time:.4f}s")
    
    # --- 2. Compilation ---
    p = magneto.Pattern(scenario["pattern"], options=scenario["options"])
    
    # Si on teste WHOLE_WORD, l'insertion "PatternX" ne devrait PAS être comptée.
    # Dans ce cas, nous ajustons l'attendu à 0 pour ce test spécifique.
    if scenario["expected_mode"] == "WHOLE_WORD":
         adjusted_expected = 0 # Car le fichier est rempli de PatternX, non Pattern
    else:
         adjusted_expected = expected_matches

    # --- 3. Exécution du Scan ---
    total_matches = 0
    global_offset = 0
    found_offsets = []
    
    scan_start_time = time.time()
    
    with open(FILE_PATH, 'rb') as f:
        while True:
            block = f.read(BLOCK_SIZE)
            if not block:
                break

            # SCANNER AVEC L'ÉTAT PERSISTANT
            matches_in_block = p.scan(block, max_matches=expected_matches + 10)
            
            for offset in matches_in_block:
                global_match_pos = global_offset + offset
                found_offsets.append(global_match_pos)
                total_matches += 1

            global_offset += len(block)
            
    scan_time = time.time() - scan_start_time
    scan_speed_mbps = (final_file_size / (1024 * 1024)) / scan_time
    
    # --- 4. Validation et Rapport ---
    
    is_success = total_matches == adjusted_expected
    status = "SUCCÈS" if is_success else "ÉCHEC"

    print("\n--- RAPPORT MAGNETO ---")
    print(f"Statut du test: {status}")
    print(f"Motif: '{scenario['pattern']}' | Options: {scenario['options']}")
    print(f"Matchs trouvés: {total_matches} | Matchs attendus: {adjusted_expected}")
    # Affiche la vitesse du moteur pour juger de la performance
    print(f"Vitesse de scan: {scan_speed_mbps:.2f} Mo/s")
    
    # Test secondaire : vérifier si find_first et count fonctionnent (non-streaming)
    p.reset_state() # Réinitialiser l'état
    quick_count = p.count(open(FILE_PATH, 'rb').read())
    print(f"Validation count(): {quick_count} (Doit être {total_matches})")
    
    # Nettoyage
    os.remove(FILE_PATH)
    
    return is_success

# =========================================================================
# EXÉCUTION DE TOUS LES SCÉNARIOS
# =========================================================================

if __name__ == "__main__":
    
    all_success = True
    
    for i, scenario in enumerate(SCENARIOS):
        if not run_test(scenario, i):
            all_success = False
            
    if all_success:
        print("\n\n#####################################################")
        print("# TOUS LES TESTS MAGNETO ONT RÉUSSI À PLEINE PUISSANCE #")
        print("#####################################################")
    else:
        print("\n\n#####################################################")
        print("# AVERTISSEMENT : CERTAINS TESTS MAGNETO ONT ÉCHOUÉ #")
        print("#####################################################")