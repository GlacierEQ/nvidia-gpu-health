# NVIDIA GPU Health — Local Health-Policy Exhibit

> **Independent GlacierEQ portfolio work. Not affiliated with, endorsed by, or connected to NVIDIA.**

This repository demonstrates deterministic **local GPU-health scoring** from synthetic or caller-supplied temperature, power, utilization, ECC-count, and modeled link-bandwidth inputs. It does **not** collect NVIDIA telemetry or control GPU hardware.

## Verified local mechanisms

- `src/gpu_health.py` validates finite sample inputs and evaluates an explicit illustrative thermal/power/ECC policy.
- The Python result exposes a bounded `health_index`, `NOMINAL | WARNING | CRITICAL` state, thermal margin, power ratio, workload context, an evidence token, and `operational_authority: false`.
- `src/nvlink_health.c` implements a small C11 policy evaluator for caller-supplied ECC counts and modeled link bandwidth.
- The native C self-test covers nominal, warning, critical, and malformed-input paths.
- `simulate_rack()` creates deterministic synthetic fixtures; it is not a telemetry collector.

## Evidence boundary

`LOCAL_SYNTHETIC_GPU_HEALTH_MODEL_NOT_NVIDIA_TELEMETRY_AUTHORITY`

Current proof may establish local deterministic computation and tests. It does **not** establish:

- NVIDIA affiliation, employment, endorsement, or proprietary access;
- NVML/DCGM/NVLink hardware telemetry acquisition;
- real-time cluster monitoring or background-daemon deployment;
- physical GPU diagnosis, failure prediction, isolation, or remediation;
- measured runtime overhead, production scale, or reliability;
- a live MCP tool, APEX Highway connection, Mastermind runtime connection, or external provider integration;
- hardware commands, scheduler authority, or production operational authority.

`mastermind_sidecar.py` is only a local process-status helper. Its presence does not establish a network or agent-mesh connection.

## Run the proof locally

```bash
PYTHONPATH=src python -m unittest discover -s tests -p 'test_*.py' -v
cc -std=c11 -Wall -Wextra -Werror -pedantic src/nvlink_health.c -lm -o /tmp/gpu_health_native
/tmp/gpu_health_native
```

The repository-owned verification script runs the Python suite, public-boundary checks, and the compiled C11 self-test in CI on the canonical `master` branch.
