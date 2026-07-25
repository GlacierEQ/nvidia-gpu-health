# Issue Contract — `nvidia-gpu-health`

## Pain
Need a single health index from thermal/power/occupancy-style signals.

## Claim
Health scorer degrades under high temp/power stress vs nominal.

## Proof
```bash
python3 job-app/helix/proofs/proof_gpu_health.py
```

## Done when
Proof exits 0. Architecture (strand/integrity/helix) is **not** a substitute for this proof.

## Anti-claim
Not live DCGM fleet product.
