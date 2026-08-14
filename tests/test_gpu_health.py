from __future__ import annotations

import math
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from gpu_health import (
    DEFAULT_POLICY,
    EVIDENCE_STATE,
    GpuSample,
    health_index,
    simulate_rack,
)


class GPUHealthTests(unittest.TestCase):
    def test_nominal_sample_is_bounded_and_non_operational(self) -> None:
        health = health_index(
            GpuSample(temp_c=55, power_w=400, sm_util=0.5, mem_util=0.4)
        )
        self.assertEqual(health["status"], "NOMINAL")
        self.assertGreaterEqual(health["health_index"], 0.0)
        self.assertLessEqual(health["health_index"], 1.0)
        self.assertEqual(health["evidence_state"], EVIDENCE_STATE)
        self.assertFalse(health["operational_authority"])

    def test_temperature_warning_and_critical_are_explicit(self) -> None:
        warning = health_index(
            GpuSample(
                temp_c=DEFAULT_POLICY.warning_temp_c,
                power_w=500,
                sm_util=0.8,
                mem_util=0.7,
            )
        )
        critical = health_index(
            GpuSample(
                temp_c=DEFAULT_POLICY.critical_temp_c,
                power_w=500,
                sm_util=0.8,
                mem_util=0.7,
            )
        )
        self.assertEqual(warning["status"], "WARNING")
        self.assertEqual(critical["status"], "CRITICAL")
        self.assertGreater(warning["health_index"], critical["health_index"])

    def test_ecc_and_power_policy_surface_warning_or_critical(self) -> None:
        ecc_warning = health_index(
            GpuSample(temp_c=60, power_w=400, sm_util=0.5, mem_util=0.4, ecc_count=1)
        )
        ecc_critical = health_index(
            GpuSample(temp_c=60, power_w=400, sm_util=0.5, mem_util=0.4, ecc_count=10)
        )
        power_warning = health_index(
            GpuSample(temp_c=60, power_w=900, sm_util=0.5, mem_util=0.4),
            tdp_w=700,
        )
        self.assertEqual(ecc_warning["status"], "WARNING")
        self.assertEqual(ecc_critical["status"], "CRITICAL")
        self.assertEqual(power_warning["status"], "WARNING")

    def test_malformed_samples_fail_closed(self) -> None:
        bad_samples = (
            GpuSample(temp_c=math.nan, power_w=400, sm_util=0.5, mem_util=0.4),
            GpuSample(temp_c=50, power_w=-1, sm_util=0.5, mem_util=0.4),
            GpuSample(temp_c=50, power_w=400, sm_util=1.1, mem_util=0.4),
            GpuSample(temp_c=50, power_w=400, sm_util=0.5, mem_util=0.4, ecc_count=-1),
            GpuSample(temp_c=50, power_w=400, sm_util=0.5, mem_util=0.4, ecc_count=True),
        )
        for sample in bad_samples:
            with self.subTest(sample=sample):
                with self.assertRaises(ValueError):
                    health_index(sample)
        with self.assertRaises(ValueError):
            health_index(
                GpuSample(temp_c=50, power_w=400, sm_util=0.5, mem_util=0.4),
                tdp_w=0,
            )

    def test_synthetic_rack_is_deterministic_and_validated(self) -> None:
        self.assertEqual(simulate_rack(3, 0.8), simulate_rack(3, 0.8))
        self.assertTrue(all(not row["operational_authority"] for row in simulate_rack(3, 0.8)))
        with self.assertRaises(ValueError):
            simulate_rack(-1, 0.8)
        with self.assertRaises(ValueError):
            simulate_rack(1, 1.1)


if __name__ == "__main__":
    unittest.main()
