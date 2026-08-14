#!/usr/bin/env bash
set -euo pipefail

ROOT="${GITHUB_WORKSPACE:-$(pwd)}"
export PYTHONPATH="$ROOT/src"

python -m compileall -q src tests mastermind_sidecar.py
python -m unittest discover -s tests -p 'test_*.py' -v

python - <<'PY'
from gpu_health import EVIDENCE_STATE, GpuSample, health_index, simulate_rack

nominal = health_index(GpuSample(temp_c=55, power_w=400, sm_util=0.5, mem_util=0.4))
assert nominal["status"] == "NOMINAL"
assert nominal["evidence_state"] == EVIDENCE_STATE
assert nominal["operational_authority"] is False
assert all(row["operational_authority"] is False for row in simulate_rack(3, 0.8))
print({"evidence_state": EVIDENCE_STATE, "nominal": nominal})
PY

cc -std=c11 -Wall -Wextra -Werror -pedantic src/nvlink_health.c -lm -o /tmp/nvidia_gpu_health_native
native_output="$(/tmp/nvidia_gpu_health_native)"
grep -Fq 'LOCAL_SYNTHETIC_GPU_HEALTH_MODEL_NOT_NVIDIA_TELEMETRY_AUTHORITY' <<<"$native_output"
grep -Fq 'operational_authority=false' <<<"$native_output"

python - <<'PY'
import json
from pathlib import Path

root = Path('.')
readme = (root / 'README.md').read_text(encoding='utf-8')
capabilities = json.loads((root / 'machine/capabilities.json').read_text())
state = json.loads((root / 'machine/excellence-state.json').read_text())
contract = json.loads((root / 'machine/target-contract.json').read_text())
expected = [
    'deterministic-synthetic-gpu-health-scoring',
    'validated-thermal-power-ecc-policy-evaluation',
    'modeled-link-bandwidth-threshold-evaluation',
    'native-c11-gpu-health-policy-self-test',
]
assert capabilities['capabilities'] == expected
assert capabilities['operational_authority'] is False
assert state['principal_state'] == 'FUNCTIONAL_CANDIDATE'
assert state['evidence_state'] == 'IMPLEMENTED_CURRENT_HEAD_NATIVE_PROOF_REQUIRED'
assert contract['current']['operational_authority'] is False
assert 'Not affiliated with, endorsed by, or connected to NVIDIA' in readme
for forbidden in (
    'tracking NVLink interconnect bandwidth and ECC memory errors in real time',
    'Zero-overhead execution',
    'Connected to APEX Highway mesh',
):
    assert forbidden not in readme
print({'public_truth': 'PASS', 'capabilities': expected})
PY
