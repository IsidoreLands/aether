# /home/isidore-admin/aether/test_aether_lang.py
import unittest
import random
import timeit

# Import all necessary components
from aether_lang import (
    parse_latin_command, run_aether_command, lockers,
    AetherGrid, dynamic_chunk, triad, destruct, create,
    KNOWN_VERBS
)

class TestAetherLang(unittest.TestCase):

    def test_parser_functionality(self):
        """1.A: Test the 'Grammatical Ear' - The Parser"""
        print("\n--- Testing Parser (1.A) ---")
        verb, infl, _ = parse_latin_command("PERTURBOABAM GRIDUM")
        self.assertEqual(verb, "PERTURBO")
        self.assertEqual(infl, "ABAM")
        print("✓ Parser handles root and inflection correctly.")

    def test_full_command_execution(self):
        """3.A: Test the 'Aetheric Sentence' - Full Command Execution"""
        print("\n--- Testing Full Command Execution (3.A) ---")
        random.seed(42)
        echo, _ = run_aether_command("PERTURBOO 10 20 30")
        self.assertEqual(echo, "PERTURBOO FLUXUM 7.26")
        print(f"✓ PERTURBO command OK: Echo '{echo}'")

        echo, _, locker_data = run_aether_command("TOGGEOO 100")
        self.assertEqual(echo, "TOGGEOO 10 APERTOS")
        self.assertEqual(locker_data[0], 10)
        print(f"✓ TOGGEO command OK: Echo affirms synthesis.")

    def test_determinism(self):
        """3.B: Test Metaphysical Safeguards - Classical Determinism"""
        print("\n--- Testing Determinism (3.B) ---")
        count, positions = lockers(100)
        self.assertEqual(count, 10)
        self.assertEqual(positions, [1, 4, 9, 16, 25, 36, 49, 64, 81, 100])
        print("✓ Classical determinism of locker problem verified.")

    def test_inflection_mods(self):
        """Test Flux Modalities via Inflections"""
        print("\n--- Testing Inflections ---")
        random.seed(101)
        _, energy_standard = run_aether_command("PERTURBOO 1 2 3")
        random.seed(101)
        _, energy_amplified = run_aether_command("PERTURBOABAM 1 2 3")
        self.assertGreater(energy_amplified, energy_standard)
        print("✓ Inflections correctly modulate flux vitality.")

    def test_chunk_triad(self):
        """Test Irreducible Non-Unity in Chunking/Triad"""
        print("\n--- Testing Non-Unity (3 Min) ---")
        chunks = dynamic_chunk([1, 2])
        self.assertEqual(len(chunks[0]), 3)
        with self.assertRaisesRegex(ValueError, "TRIAD REQUIRET TRES ARGUMENTA"):
            triad([1, 2], 1.0)
        print("✓ Triadic stability enforced.")

    def test_dialectic(self):
        """Test Boyd-Inspired Destruction/Creation"""
        print("\n--- Testing Dialectic Phases ---")
        grid = AetherGrid()
        destruct(grid)
        self.assertNotEqual(grid.energy, 0)
        create(grid)
        self.assertLess(grid.energy, 10)
        print("✓ Dialectic cycles offset entropy.")

    def test_undefinability(self):
        """Test Tarski Safeguard for Self-Reference"""
        print("\n--- Testing Tarski Safeguard ---")
        with self.assertRaisesRegex(ValueError, "TARSKI ERRORUM"):
            run_aether_command("VERITAS SELF")
        print("✓ Self-truth undefinable—error raised correctly.")

    def test_fuzz(self):
        """Test system resilience with random valid commands."""
        print("\n--- Fuzz Testing ---")
        test_verbs = ['PERTURBO', 'CONVERGO']
        for _ in range(500):
            verb = random.choice(test_verbs)
            infl = random.choice(['O', 'E', 'ABAM', 'EBAM', 'AM', ''])
            args = [str(random.randint(1, 10)) for _ in range(random.randint(3, 5))]
            cmd = f"{verb}{infl} {' '.join(args)}"
            
            # MODIFICATION: The test must anticipate the interpreter's default inflection logic.
            expected_infl = infl if infl else 'O'
            
            try:
                echo, _ = run_aether_command(cmd)
                self.assertTrue(echo.startswith(f"{verb}{expected_infl} FLUXUM"))
            except Exception as e:
                self.fail(f"Fuzz test failed with unexpected error on command '{cmd}': {e}")
        print("✓ Fuzz resilient—no unhandled errors.")
    
    def test_scale(self):
        """Test performance on larger computations."""
        print("\n--- Testing Scalability ---")
        exec_time = timeit.timeit(lambda: lockers(10000), number=1)
        self.assertLess(exec_time, 1.0, "lockers(10000) should be faster than 1s")
        print(f"✓ Lockers(10000) scaled efficiently ({exec_time:.4f}s).")
        grid = AetherGrid(100)
        grid.converge()
        self.assertTrue(isinstance(grid.energy, float))
        print("✓ Grid convergence scaled to 100x100.")

if __name__ == '__main__':
    unittest.main(verbosity=2)
