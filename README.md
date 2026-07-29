# NVIDIA GPU Health — NVLink & ECC Error Monitor 🟢

> **C low-overhead NVLink bandwidth evaluator and ECC memory error health monitor.**

[![C](https://img.shields.io/badge/C-11-00599C)]()
[![Python](https://img.shields.io/badge/Python-3.9+-blue)]()
[![Domain](https://img.shields.io/badge/Domain-GPU%20Diagnostics-green)]()

---

## 🎯 For Recruiters & Hiring Managers

This repository implements a **low-level C NVIDIA GPU health monitor** — tracking NVLink interconnect bandwidth and ECC memory errors in real time. It demonstrates:

- **C structural telemetry parsing** evaluating single-bit vs double-bit ECC memory errors
- **NVLink health scoring** detecting degraded interconnect lanes before node crashes occur
- **Zero-overhead execution** suitable for running as a background daemon on GPU nodes
- **Python simulation test harness** verifying health status evaluation deterministically

**Why this matters**: Uncorrected double-bit ECC errors cause immediate GPU node panics. Real-time telemetry monitoring isolates degrading GPUs before they interrupt multi-day training runs.

---

## 🔬 For Engineers & Technical Reviewers

### Core Components

| Component | Language | Purpose |
|---|---|---|
| `src/nvlink_health.c` | C | C struct and health evaluation function for NVLink & ECC |
| `tests/test_nvlink_health.py` | Python | Test wrapper simulating GPU health states |

---

## 🤖 ML/AI & Programmatic Mesh Integration

- **MCP Tool**: `gpu_health_check()` — health status inspection tool for cluster agents
- **Mastermind Sidecar**: Connected to APEX Highway mesh
- **SHA-256 Integrity**: Tracked in `.integrity/file_hashes.json`

---

## ⚡ Quick Start

```bash
python3 tests/test_nvlink_health.py
```
