"""Policy-level regression cases mirrored by the compiled C self-test."""
import math
import unittest


class LocalLinkHealthModel:
    def evaluate(
        self,
        *,
        single_bit: int,
        double_bit: int,
        bandwidth_gbps: float,
        single_bit_warning: int = 1000,
        minimum_bandwidth_gbps: float = 700.0,
    ) -> int:
        if not math.isfinite(bandwidth_gbps) or bandwidth_gbps < 0:
            return 3
        if double_bit > 0:
            return 2
        if single_bit >= single_bit_warning or bandwidth_gbps < minimum_bandwidth_gbps:
            return 1
        return 0


class TestLocalLinkHealthModel(unittest.TestCase):
    def test_nominal_warning_critical_and_invalid(self) -> None:
        model = LocalLinkHealthModel()
        self.assertEqual(model.evaluate(single_bit=12, double_bit=0, bandwidth_gbps=900), 0)
        self.assertEqual(model.evaluate(single_bit=1000, double_bit=0, bandwidth_gbps=900), 1)
        self.assertEqual(model.evaluate(single_bit=0, double_bit=0, bandwidth_gbps=650), 1)
        self.assertEqual(model.evaluate(single_bit=0, double_bit=1, bandwidth_gbps=900), 2)
        self.assertEqual(model.evaluate(single_bit=0, double_bit=0, bandwidth_gbps=math.nan), 3)


if __name__ == "__main__":
    unittest.main()
