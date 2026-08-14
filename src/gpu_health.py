#!/usr/bin/env python3
"""Deterministic local GPU health scoring for synthetic or caller-supplied samples.

This module does not read NVIDIA telemetry, control hardware, diagnose physical
failures, or provide operational cluster authority.
"""
from __future__ import annotations

import math
from dataclasses import dataclass

EVIDENCE_STATE = "LOCAL_SYNTHETIC_GPU_HEALTH_MODEL_NOT_NVIDIA_TELEMETRY_AUTHORITY"


@dataclass(frozen=True)
class GpuSample:
    temp_c: float
    power_w: float
    sm_util: float
    mem_util: float
    ecc_count: int = 0


@dataclass(frozen=True)
class HealthPolicy:
    warning_temp_c: float = 83.0
    critical_temp_c: float = 89.0
    max_power_ratio: float = 1.20
    ecc_warning_count: int = 1
    ecc_critical_count: int = 10


DEFAULT_POLICY = HealthPolicy()
TARGET_MAX_C = 55.0
THROTTLE_C = DEFAULT_POLICY.warning_temp_c
HARD_LIMIT_C = DEFAULT_POLICY.critical_temp_c


def _bounded(value: float) -> float:
    return max(0.0, min(1.0, value))


def _validate_policy(policy: HealthPolicy) -> None:
    numeric = (
        policy.warning_temp_c,
        policy.critical_temp_c,
        policy.max_power_ratio,
    )
    if not all(math.isfinite(value) for value in numeric):
        raise ValueError("policy values must be finite")
    if policy.critical_temp_c <= policy.warning_temp_c:
        raise ValueError("critical temperature must exceed warning temperature")
    if policy.max_power_ratio <= 0:
        raise ValueError("max power ratio must be positive")
    if isinstance(policy.ecc_warning_count, bool) or isinstance(policy.ecc_critical_count, bool):
        raise ValueError("ECC limits must be integers")
    if policy.ecc_warning_count < 0 or policy.ecc_critical_count <= policy.ecc_warning_count:
        raise ValueError("ECC critical limit must exceed the non-negative warning limit")


def _validate_sample(sample: GpuSample, tdp_w: float) -> None:
    numeric = (sample.temp_c, sample.power_w, sample.sm_util, sample.mem_util, tdp_w)
    if not all(math.isfinite(value) for value in numeric):
        raise ValueError("sample and TDP values must be finite")
    if sample.power_w < 0 or tdp_w <= 0:
        raise ValueError("power must be non-negative and TDP must be positive")
    if not 0.0 <= sample.sm_util <= 1.0 or not 0.0 <= sample.mem_util <= 1.0:
        raise ValueError("utilization values must be in 0..1")
    if isinstance(sample.ecc_count, bool) or not isinstance(sample.ecc_count, int):
        raise ValueError("ECC count must be a non-boolean integer")
    if sample.ecc_count < 0:
        raise ValueError("ECC count must be non-negative")


def thermal_margin(temp_c: float, policy: HealthPolicy = DEFAULT_POLICY) -> float:
    """Return modeled degrees remaining before the illustrative critical threshold."""
    _validate_policy(policy)
    if not math.isfinite(temp_c):
        raise ValueError("temperature must be finite")
    return policy.critical_temp_c - temp_c


def anomaly_score(z: float) -> float:
    """Return a bounded local attenuation factor for a positive modeled excursion."""
    if not math.isfinite(z):
        raise ValueError("excursion must be finite")
    return math.exp(-0.5 * max(0.0, z) ** 2)


def health_index(
    sample: GpuSample,
    tdp_w: float = 700.0,
    policy: HealthPolicy = DEFAULT_POLICY,
) -> dict:
    """Evaluate a deterministic local health score under explicit illustrative policy."""
    _validate_policy(policy)
    _validate_sample(sample, tdp_w)

    power_ratio = sample.power_w / tdp_w
    thermal_span = policy.critical_temp_c - policy.warning_temp_c
    if sample.temp_c <= policy.warning_temp_c:
        thermal_factor = 1.0
    else:
        thermal_factor = _bounded(
            (policy.critical_temp_c - sample.temp_c) / thermal_span
        )
    power_factor = _bounded(
        1.0 - max(0.0, power_ratio - policy.max_power_ratio) / policy.max_power_ratio
    )
    if sample.ecc_count >= policy.ecc_critical_count:
        ecc_factor = 0.0
    elif sample.ecc_count >= policy.ecc_warning_count:
        ecc_factor = 0.5
    else:
        ecc_factor = 1.0

    score = _bounded(0.50 * thermal_factor + 0.30 * power_factor + 0.20 * ecc_factor)

    if (
        sample.temp_c >= policy.critical_temp_c
        or sample.ecc_count >= policy.ecc_critical_count
    ):
        status = "CRITICAL"
    elif (
        sample.temp_c >= policy.warning_temp_c
        or power_ratio > policy.max_power_ratio
        or sample.ecc_count >= policy.ecc_warning_count
    ):
        status = "WARNING"
    else:
        status = "NOMINAL"

    return {
        "health_index": round(score, 4),
        "status": status,
        "thermal_margin_c": round(thermal_margin(sample.temp_c, policy), 2),
        "power_ratio": round(power_ratio, 3),
        "utilization_context": round(0.6 * sample.sm_util + 0.4 * sample.mem_util, 4),
        "evidence_state": EVIDENCE_STATE,
        "operational_authority": False,
    }


def simulate_rack(n: int = 8, load: float = 0.85) -> list[dict]:
    """Generate deterministic synthetic samples; this is not a telemetry collector."""
    if isinstance(n, bool) or not isinstance(n, int) or n < 0:
        raise ValueError("n must be a non-negative integer")
    if not math.isfinite(load) or not 0.0 <= load <= 1.0:
        raise ValueError("load must be finite and in 0..1")
    out: list[dict] = []
    for i in range(n):
        sample = GpuSample(
            temp_c=TARGET_MAX_C + load * 28.0 + (i % 3) * 2.0,
            power_w=700.0 * (0.65 + 0.30 * load),
            sm_util=load,
            mem_util=load * 0.9,
        )
        health = health_index(sample)
        health["gpu_id"] = i
        out.append(health)
    return out


if __name__ == "__main__":
    for row in simulate_rack():
        print(row)
