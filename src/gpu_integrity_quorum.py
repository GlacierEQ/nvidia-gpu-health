#!/usr/bin/env python3
"""Deterministic quorum over caller-supplied GPU health observations.

This module is a local policy exhibit. It does not read NVIDIA telemetry,
drain hardware, command schedulers, or provide cluster operational authority.
"""
from __future__ import annotations

import hashlib
import json
import math
from dataclasses import dataclass

from gpu_health import GpuSample, health_index

QUORUM_SCHEMA = "glaciereq.nvidia-gpu-health.integrity-quorum.v1"
QUORUM_EVIDENCE_STATE = (
    "LOCAL_SYNTHETIC_GPU_INTEGRITY_QUORUM_NOT_NVIDIA_CLUSTER_AUTHORITY"
)


@dataclass(frozen=True)
class IntegrityObservation:
    gpu_id: str
    sample: GpuSample
    numerics_finite: bool = True

    def validate(self) -> None:
        if not isinstance(self.gpu_id, str) or not self.gpu_id.strip():
            raise ValueError("gpu_id must be non-empty text")
        if not isinstance(self.numerics_finite, bool):
            raise ValueError("numerics_finite must be boolean")


def _digest(value: object) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def evaluate_integrity_quorum(
    observations: list[IntegrityObservation],
    *,
    tdp_w: float = 700.0,
    min_nominal_fraction: float = 0.75,
) -> dict[str, object]:
    """Aggregate local health and numerical-integrity signals into one bounded result."""

    if not observations:
        raise ValueError("at least one observation is required")
    if not math.isfinite(min_nominal_fraction) or not 0.0 <= min_nominal_fraction <= 1.0:
        raise ValueError("min_nominal_fraction must be finite and in 0..1")

    seen: set[str] = set()
    members: list[dict[str, object]] = []
    nominal = warning = critical = 0
    review_candidates: list[str] = []

    for observation in observations:
        observation.validate()
        if observation.gpu_id in seen:
            raise ValueError("gpu_id values must be unique")
        seen.add(observation.gpu_id)

        health = health_index(observation.sample, tdp_w=tdp_w)
        health_state = str(health["status"])
        if not observation.numerics_finite:
            member_state = "CRITICAL"
            reason = "caller-supplied numerical-integrity signal is non-finite"
        elif health_state == "CRITICAL":
            member_state = "CRITICAL"
            reason = "local health policy is critical"
        elif health_state == "WARNING":
            member_state = "WARNING"
            reason = "local health policy requires review"
        else:
            member_state = "NOMINAL"
            reason = "local health policy is nominal"

        if member_state == "CRITICAL":
            critical += 1
            review_candidates.append(observation.gpu_id)
        elif member_state == "WARNING":
            warning += 1
            review_candidates.append(observation.gpu_id)
        else:
            nominal += 1

        members.append(
            {
                "gpu_id": observation.gpu_id,
                "state": member_state,
                "reason": reason,
                "numerics_finite": observation.numerics_finite,
                "health_index": health["health_index"],
                "thermal_margin_c": health["thermal_margin_c"],
                "power_ratio": health["power_ratio"],
            }
        )

    total = len(members)
    nominal_fraction = nominal / total
    if critical:
        state = "CRITICAL"
    elif warning or nominal_fraction < min_nominal_fraction:
        state = "WARNING"
    else:
        state = "NOMINAL"

    body: dict[str, object] = {
        "schema": QUORUM_SCHEMA,
        "state": state,
        "counts": {
            "nominal": nominal,
            "warning": warning,
            "critical": critical,
            "total": total,
        },
        "nominal_fraction": round(nominal_fraction, 4),
        "min_nominal_fraction": min_nominal_fraction,
        "review_candidates": sorted(review_candidates),
        "members": members,
        "evidence_state": QUORUM_EVIDENCE_STATE,
        "operational_authority": False,
        "hardware_action": False,
    }
    body["receipt_sha256"] = _digest(body)
    return body
