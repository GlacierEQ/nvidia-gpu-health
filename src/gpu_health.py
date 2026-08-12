#!/usr/bin/env python3
"""NVIDIA-class GPU health model — portfolio motion (not NVIDIA employment).

First-principles thermal/power/occupancy signals for interviewable demos.
Exact SI constants and explicit portfolio assumptions.
"""
from __future__ import annotations

import math
from dataclasses import dataclass

STEFAN_BOLTZMANN = 5.670374419e-8
G = 9.80665
THERMAL_ANOMALY_SIGMA = math.e
CONFIDENCE_FLOOR = 0.31415
FLUX_THRESHOLD = 1.21
THROTTLE_C = 83.0  # H100-class onset (portfolio constant)
HARD_LIMIT_C = 89.0
TARGET_MAX_C = 55.0  # preferred operating-zone ceiling °C


@dataclass
class GpuSample:
    temp_c: float
    power_w: float
    sm_util: float  # 0..1
    mem_util: float  # 0..1
    ecc_count: int = 0


def thermal_margin(temp_c: float) -> float:
    """°C remaining before hard limit."""
    return HARD_LIMIT_C - temp_c


def anomaly_score(z: float) -> float:
    """Return bounded confidence for a positive thermal excursion in sigma units."""
    score = math.exp(-0.5 * (max(0.0, z) / THERMAL_ANOMALY_SIGMA) ** 2)
    return max(CONFIDENCE_FLOOR, score)


def health_index(sample: GpuSample, tdp_w: float = 700.0) -> dict:
    """Composite health 0..1 with explicit status for demos.

    ``TARGET_MAX_C`` is a ceiling, not an ideal point. Temperatures at or below it
    therefore receive full thermal confidence; only excursions above the ceiling
    decay confidence.
    """
    margin = thermal_margin(sample.temp_c)
    power_ratio = sample.power_w / max(tdp_w, 1.0)
    thermal_excursion_sigma = max(0.0, sample.temp_c - TARGET_MAX_C) / THERMAL_ANOMALY_SIGMA
    conf = anomaly_score(thermal_excursion_sigma)
    util = 0.6 * sample.sm_util + 0.4 * sample.mem_util
    thermal_term = max(0.0, min(1.0, margin / (HARD_LIMIT_C - TARGET_MAX_C)))
    power_term = max(0.0, 1.0 - max(0.0, power_ratio - 1.0))
    ecc_penalty = 0.15 if sample.ecc_count else 0.0
    index = conf * (0.45 * thermal_term + 0.25 * power_term + 0.30 * util) - ecc_penalty
    index = max(0.0, min(1.0, index))
    if sample.temp_c >= HARD_LIMIT_C or sample.ecc_count > 10:
        status = "CRITICAL"
    elif sample.temp_c >= THROTTLE_C or power_ratio > FLUX_THRESHOLD:
        status = "THROTTLE_RISK"
    elif sample.temp_c <= TARGET_MAX_C and sample.ecc_count == 0:
        status = "OPTIMAL"
    else:
        status = "NOMINAL"
    return {
        "health_index": round(index, 4),
        "status": status,
        "thermal_margin_c": round(margin, 2),
        "power_ratio": round(power_ratio, 3),
        "confidence": round(conf, 4),
    }


def simulate_rack(n: int = 8, load: float = 0.85) -> list[dict]:
    out = []
    for i in range(n):
        temp = TARGET_MAX_C + load * 35 + (i % 3) * 2.5
        power = 700 * (0.7 + 0.3 * load)
        sample = GpuSample(
            temp_c=temp,
            power_w=power,
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
