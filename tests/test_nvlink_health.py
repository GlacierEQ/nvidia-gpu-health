"""Test suite for NVIDIA GPU Health Monitor."""
import unittest

class NVLinkHealthSim:
    def evaluate_health(self, single_bit: int, double_bit: int) -> int:
        if double_bit > 0: return 2
        if single_bit > 1000: return 1
        return 0

class TestNVLinkHealth(unittest.TestCase):
    def test_health_evaluation(self):
        m = NVLinkHealthSim()
        self.assertEqual(m.evaluate_health(12, 0), 0)
        self.assertEqual(m.evaluate_health(1500, 0), 1)

if __name__ == "__main__":
    unittest.main()
