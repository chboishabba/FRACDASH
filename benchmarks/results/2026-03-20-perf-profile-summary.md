# FRACDASH CPU/GPU Profiling Decision

## Bottom Line

- CPU: `cpu-baseline-still-has-obvious-gap`
- GPU: `warm-resident-gpu-win-is-real`

## Obvious Now
- tighten GPU routing around warm-resident wins
- profile-based GPU host/setup reduction

## CPU Read

- `compiled` wins all sampled exact-step cases: `False`
- obvious large CPU gain over imported baseline: `True`

## GPU Read

- warm GPU-preferred cases: `44`
- cold-start penalty cases: `21`

## Next Performance Focus

- refine the warm-resident GPU routing boundary
- reduce host/setup overhead on the GPU path before attempting deeper kernel changes
- only return to CPU exact-step tuning if a new profiling run surfaces a fresh dominant hotspot or a new workload where `compiled` clearly loses
