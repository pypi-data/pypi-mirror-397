import magneto
import unittest
import sys

class MagnetoRobustnessTest(unittest.TestCase):
    
    def test_pattern_too_long(self):
        """Vérifie si la compilation échoue pour un motif > 64 caractères."""
        long_pattern = "A" * 65
        
        # Le code C magneto.c est censé renvoyer MAGNETO_ERR_PATTERN_TOO_LONG.
        # Ce test vérifie que l'API Python le traduit en ValueError.
        with self.assertRaises(ValueError) as context:
            magneto.Pattern(long_pattern)
        
        # Vérifie le message d'erreur exact pour s'assurer que l'erreur C a été interceptée
        self.assertIn("Motif trop long (max 64 caractères).", str(context.exception))
        
        print(f"✅ Test Motif Trop Long (65 chars) réussi.")

    def test_pattern_empty(self):
        """Vérifie si la compilation échoue pour un motif vide."""
        empty_pattern = ""
        
        with self.assertRaises(ValueError) as context:
            magneto.Pattern(empty_pattern)
            
        self.assertIn("Motif vide.", str(context.exception))
        
        print(f"✅ Test Motif Vide réussi.")
        
    def test_invalid_option_combination(self):
        """Vérifie la gestion d'une combinaison d'options invalide."""
        
        # Test non implémenté pour l'instant car toutes les options actuelles sont compatibles.
        # Si vous ajoutez une option incompatible, ce test est indispensable.
        # Par exemple, si vous ajoutez OPTION_FLOU et OPTION_EXACT qui seraient mutuellement exclusives.
        
        print(f"✅ Test Options Invalides: Non applicable pour la v1.0, ignoré.")


if __name__ == '__main__':
    # Empêche l'exécution de lancer le programme de test précédent par accident
    if 'test/test.py' in sys.argv:
        print("Veuillez exécuter ce script directement (python test_robustness.py) et non via l'ancien chemin.")
        sys.exit(1)
        
    unittest.main(argv=['first-arg-is-ignored'], exit=False)