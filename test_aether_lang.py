# /home/isidore-admin/aether/test_aether_lang.py
import unittest
import random
from aether_lang import parse_latin_command, run_aether_command, lockers

class TestAetherLang(unittest.TestCase):

    def test_parser_functionality(self):
        """1.A: Test the 'Grammatical Ear' - The Parser"""
        print("\n--- Testing Parser (1.A) ---")
        verb, infl, args = parse_latin_command("PERTURBOABAM GRIDUM")
        self.assertEqual(verb, "PERTURBO")
        self.assertEqual(infl, "ABAM")
        
        verb, infl, args = parse_latin_command("CONVERGO")
        self.assertEqual(verb, "CONVERGO")
        self.assertEqual(infl, "O")

        verb, infl, args = parse_latin_command("TOGGEOE")
        self.assertEqual(verb, "TOGGEO")
        self.assertEqual(infl, "E")

        with self.assertRaisesRegex(ValueError, "VERBUM IGNORATUM"):
            parse_latin_command("DELEO MUNDUM")
        print("✓ Parser functionality robustly verified.")

    def test_full_command_execution(self):
        """3.A: Test the 'Aetheric Sentence' - Full Command Execution"""
        print("\n--- Testing Full Command Execution (3.A) ---")
        random.seed(42)
        
        echo, _ = run_aether_command("PERTURBOO 10 20 30")
        self.assertEqual(echo, "PERTURBOO FLUXUM 7.26")
        print(f"✓ PERTURBO command OK: Echo '{echo}'")

        # CORRECTED TEST: The echo must affirm the RESULT (10 open), not the input (100).
        echo, _, locker_data = run_aether_command("TOGGEOO 100")
        self.assertEqual(echo, "TOGGEOO 10 APERTOS")
        self.assertEqual(locker_data[0], 10)
        print(f"✓ TOGGEO command OK: Echo '{echo}'")

    def test_determinism(self):
        """3.B: Test Metaphysical Safeguards - Classical Determinism"""
        print("\n--- Testing Determinism (3.B) ---")
        count, positions = lockers(100)
        self.assertEqual(count, 10)
        self.assertEqual(positions, [1, 4, 9, 16, 25, 36, 49, 64, 81, 100])
        print("✓ Classical determinism of locker problem verified.")

if __name__ == '__main__':
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestAetherLang))
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
