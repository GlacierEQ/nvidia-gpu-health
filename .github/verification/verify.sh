#!/usr/bin/env bash
set -euo pipefail

export PYTHONPATH="${GITHUB_WORKSPACE:-$(pwd)}/src"
python -m compileall -q src tests mastermind_sidecar.py
python -m unittest discover -s tests -p 'test_*.py' -v
python - <<'PY'
from gpu_health import GpuSample, TARGET_MAX_C, health_index

cool = health_index(GpuSample(temp_c=40, power_w=400, sm_util=0.5, mem_util=0.4))
hotter = health_index(GpuSample(temp_c=TARGET_MAX_C + 5, power_w=500, sm_util=0.8, mem_util=0.7))
assert cool['status'] == 'OPTIMAL'
assert cool['confidence'] == 1.0
assert cool['health_index'] > hotter['health_index']
print({'cool': cool, 'above_ceiling': hotter})
PY
