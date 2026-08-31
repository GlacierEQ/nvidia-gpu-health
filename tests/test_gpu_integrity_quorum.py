from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from gpu_health import GpuSample
from gpu_integrity_quorum import (
    QUORUM_EVIDENCE_STATE,
    IntegrityObservation,
    evaluate_integrity_quorum,
)


class GPUIntegrityQuorumTests(unittest.TestCase):
    def test_nominal_quorum_is_deterministic_and_non_operational(self) -> None:
        observations = [
            IntegrityObservation(
                f"gpu-{idx}",
                GpuSample(temp_c=60, power_w=450, sm_util=0.7, mem_util=0.6),
            )
            for idx in range(4)
        ]
        first = evaluate_integrity_quorum(observations)
        second = evaluate_integrity_quorum(observations)
        self.assertEqual(first, second)
        self.assertEqual(first["state"], "NOMINAL")
        self.assertEqual(first["counts"]["nominal"], 4)
        self.assertEqual(first["evidence_state"], QUORUM_EVIDENCE_STATE)
        self.assertFalse(first["operational_authority"])
        self.assertFalse(first["hardware_action"])
        self.assertEqual(len(first["receipt_sha256"]), 64)

    def test_numerical_integrity_failure_forces_critical_review(self) -> None:
        result = evaluate_integrity_quorum(
            [
                IntegrityObservation(
                    "gpu-0",
                    GpuSample(temp_c=60, power_w=450, sm_util=0.7, mem_util=0.6),
                ),
                IntegrityObservation(
                    "gpu-1",
                    GpuSample(temp_c=60, power_w=450, sm_util=0.7, mem_util=0.6),
                    numerics_finite=False,
                ),
            ]
        )
        self.assertEqual(result["state"], "CRITICAL")
        self.assertEqual(result["counts"]["critical"], 1)
        self.assertEqual(result["review_candidates"], ["gpu-1"])

    def test_warning_health_is_preserved_in_quorum(self) -> None:
        result = evaluate_integrity_quorum(
            [
                IntegrityObservation(
                    "gpu-0",
                    GpuSample(temp_c=60, power_w=450, sm_util=0.7, mem_util=0.6),
                ),
                IntegrityObservation(
                    "gpu-1",
                    GpuSample(temp_c=84, power_w=450, sm_util=0.7, mem_util=0.6),
                ),
            ]
        )
        self.assertEqual(result["state"], "WARNING")
        self.assertEqual(result["counts"]["warning"], 1)
        self.assertEqual(result["review_candidates"], ["gpu-1"])

    def test_duplicate_empty_and_invalid_policy_inputs_fail_closed(self) -> None:
        sample = GpuSample(temp_c=60, power_w=450, sm_util=0.7, mem_util=0.6)
        with self.assertRaises(ValueError):
            evaluate_integrity_quorum([])
        with self.assertRaises(ValueError):
            evaluate_integrity_quorum(
                [
                    IntegrityObservation("gpu-0", sample),
                    IntegrityObservation("gpu-0", sample),
                ]
            )
        with self.assertRaises(ValueError):
            evaluate_integrity_quorum(
                [IntegrityObservation("gpu-0", sample)],
                min_nominal_fraction=1.1,
            )
        with self.assertRaises(ValueError):
            evaluate_integrity_quorum(
                [IntegrityObservation("", sample)]
            )


if __name__ == "__main__":
    unittest.main()
