from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from gpu_health import GpuSample, TARGET_MAX_C, THROTTLE_C, health_index


class GPUHealthTests(unittest.TestCase):
    def test_cool_sample_is_not_penalized_for_being_below_ceiling(self) -> None:
        health = health_index(
            GpuSample(temp_c=40, power_w=400, sm_util=0.5, mem_util=0.4)
        )
        self.assertEqual(health["status"], "OPTIMAL")
        self.assertEqual(health["confidence"], 1.0)
        self.assertGreater(health["health_index"], 0.3)

    def test_crossing_preferred_ceiling_reduces_confidence(self) -> None:
        at_ceiling = health_index(
            GpuSample(
                temp_c=TARGET_MAX_C,
                power_w=500,
                sm_util=0.8,
                mem_util=0.7,
            )
        )
        above_ceiling = health_index(
            GpuSample(
                temp_c=TARGET_MAX_C + 5,
                power_w=500,
                sm_util=0.8,
                mem_util=0.7,
            )
        )
        self.assertEqual(at_ceiling["confidence"], 1.0)
        self.assertLess(above_ceiling["confidence"], at_ceiling["confidence"])
        self.assertLess(above_ceiling["health_index"], at_ceiling["health_index"])

    def test_throttle_threshold_surfaces_risk(self) -> None:
        health = health_index(
            GpuSample(
                temp_c=THROTTLE_C + 1,
                power_w=750,
                sm_util=0.95,
                mem_util=0.9,
            )
        )
        self.assertIn(health["status"], ("THROTTLE_RISK", "CRITICAL"))


if __name__ == "__main__":
    unittest.main()
