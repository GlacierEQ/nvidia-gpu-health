from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOKEN = "LOCAL_SYNTHETIC_GPU_HEALTH_MODEL_NOT_NVIDIA_TELEMETRY_AUTHORITY"
EXPECTED_CAPABILITIES = [
    "deterministic-synthetic-gpu-health-scoring",
    "validated-thermal-power-ecc-policy-evaluation",
    "modeled-link-bandwidth-threshold-evaluation",
    "native-c11-gpu-health-policy-self-test",
    "deterministic-synthetic-multi-gpu-integrity-quorum",
    "caller-supplied-numerical-integrity-fail-closed",
]


class PublicTruthTests(unittest.TestCase):
    def test_readme_is_independent_and_non_operational(self) -> None:
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("Not affiliated with, endorsed by, or connected to NVIDIA", readme)
        self.assertIn(TOKEN, readme)
        self.assertIn("does **not** collect NVIDIA telemetry", readme)
        self.assertNotIn("tracking NVLink interconnect bandwidth and ECC memory errors in real time", readme)
        self.assertNotIn("Zero-overhead execution", readme)
        self.assertNotIn("Connected to APEX Highway mesh", readme)

    def test_machine_surface_fails_closed_to_exact_capabilities(self) -> None:
        capabilities = json.loads((ROOT / "machine/capabilities.json").read_text())
        state = json.loads((ROOT / "machine/excellence-state.json").read_text())
        contract = json.loads((ROOT / "machine/target-contract.json").read_text())
        self.assertEqual(capabilities["capabilities"], EXPECTED_CAPABILITIES)
        self.assertEqual(capabilities["evidence_state"], TOKEN)
        self.assertFalse(capabilities["operational_authority"])
        self.assertEqual(state["principal_state"], "FUNCTIONAL_CANDIDATE")
        self.assertEqual(state["evidence_state"], "IMPLEMENTED_CURRENT_HEAD_NATIVE_PROOF_REQUIRED")
        self.assertFalse(contract["current"]["operational_authority"])

    def test_python_and_c_sources_share_evidence_boundary(self) -> None:
        python_source = (ROOT / "src/gpu_health.py").read_text(encoding="utf-8")
        quorum_source = (ROOT / "src/gpu_integrity_quorum.py").read_text(encoding="utf-8")
        c_source = (ROOT / "src/nvlink_health.c").read_text(encoding="utf-8")
        self.assertIn(TOKEN, python_source)
        self.assertIn("LOCAL_SYNTHETIC_GPU_INTEGRITY_QUORUM_NOT_NVIDIA_CLUSTER_AUTHORITY", quorum_source)
        self.assertIn('"operational_authority": False', quorum_source)
        self.assertIn(TOKEN, c_source)
        self.assertIn('"operational_authority": False', python_source)
        self.assertIn('operational_authority=false', c_source)

    def test_sidecar_is_not_presented_as_network_integration(self) -> None:
        sidecar = (ROOT / "mastermind_sidecar.py").read_text(encoding="utf-8")
        self.assertNotIn("requests", sidecar)
        self.assertNotIn("http://", sidecar)
        self.assertNotIn("https://", sidecar)
        self.assertNotIn("socket", sidecar)


if __name__ == "__main__":
    unittest.main()
