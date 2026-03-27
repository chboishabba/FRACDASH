# DA51 Below-Shard Contract

This note freezes the current inner-payload contract for the checked-in
`../dashi_agda/da51_shards/*.cbor` corpus and its Agda mirror in
[`PerfHistory.agda`](/home/c/Documents/code/dashi_agda/PerfHistory.agda).

The purpose is narrow:

- govern below-shard modeling and compression work in `FRACDASH`
- distinguish the shipped shard contract from the current generator source
- keep exact-reconstruction claims scoped to the artifact shape that actually
  exists on disk

## Canonical Source For This Lane

Treat these as canonical for below-shard work:

- [`../dashi_agda/da51_shards/`](/home/c/Documents/code/dashi_agda/da51_shards)
- [`../dashi_agda/PerfHistory.agda`](/home/c/Documents/code/dashi_agda/PerfHistory.agda)

Do not treat [`../dashi_agda/perf_da51.py`](/home/c/Documents/code/dashi_agda/perf_da51.py)
as canonical for the inner-payload contract on its own.

Reason:

- `perf_da51.py` currently emits only `file`, `sha256`, `counters`, and
  `trace_sha256`
- the shipped shards and `PerfHistory.agda` also contain a `fractran` payload
- so the generator source is stale or incomplete relative to the checked-in
  artifact surface for this lane

## Current Top-Level Shard Shape

All current shards use DA51 CBOR tag `55889` and carry:

- `file`
- `sha256`
- `counters`
- `trace_sha256`
- `fractran`

`trace_sha256` is currently not a hash of the FRACTRAN trace. It is exactly the
SHA-256 of the sorted `counters` JSON payload, matching the implementation in
[`perf_da51.py`](/home/c/Documents/code/dashi_agda/perf_da51.py).

## Current FRACTRAN Variants

### Positive FRACTRAN shape

Observed in `40` current shards.

Fields:

- `ssp_primes`
- `state`
- `denominators`
- `fractions`
- `trace`
- `steps`
- `earns_moonshine`

Additional current invariants of the shipped corpus:

- `fractions` always has length `3`
- numerators are always `(47, 59, 71)`
- `trace` is exactly derivable from `state + fractions + steps`
- `steps = 3`
- `earns_moonshine = True`

Only the denominators vary across the current positive family.

### Negative / exception shape

Observed in `1` current shard: `MonsterVectors.cbor`.

Fields:

- `ssp_primes`
- `state`
- `earns_moonshine`
- `reason`

Current negative case:

- `state = null`
- `earns_moonshine = False`
- `reason = "only 2 SSP primes < 47"`

## Below-Shard Work Scope

Below-shard modeling in `FRACDASH` may treat these as derivable for the current
shipped corpus:

- positive-case `fractions` from fixed numerators plus stored denominators
- positive-case `trace` from deterministic FRACTRAN execution
- `trace_sha256` from `counters`

Any exact-reconstruction claim must decode back to the original shard bytes for
the current checked-in corpus.

If future JMD artifacts add richer perf or trace payloads, this contract must be
reopened rather than silently stretched.
