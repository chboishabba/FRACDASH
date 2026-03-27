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

Temporary reconciliation path (2026-03-27):

- `../dashi_agda/perf_da51.py` now supports `--fractran-template`, which copies
  a `fractran` payload by file name from an existing shard directory when
  generating fresh shards.
- this keeps legacy output unchanged unless the flag is explicitly enabled, so
  existing local workflows remain stable while a full contract migration is being
  decided upstream.

## Source-File Boundary Map

To keep upstreaming and local implementation aligned, this is the authoritative
below-shard boundary mapping:

- `../dashi_agda/perf_da51.py`
  - `da51_shard(...)` currently emits only:
    - `file`
    - `sha256`
    - `counters`
    - `trace_sha256`
  - it writes to `../dashi_agda/da51_shards`
  - it does not emit `fractran`, so it is incomplete as a canonical description of
    the currently shipped payload
- `../dashi_agda/PerfHistory.agda`
  - `shard-0` .. `shard-39` provide the checked-in payload mirror with
    full fields:
    - `file`
    - `sha256`
    - `counters`
    - `trace_sha256`
    - `fractran`
- `../dashi_agda/da51_shards/*.cbor`
  - `41` checked-in payload files plus one `summary.json`
  - `40` files are positive FRACTRAN rows with explicit `denominators`,
    `fractions`, `trace`, `steps`, `earns_moonshine`
  - `1` file is a negative exception (`MonsterVectors.cbor`) with only `ssp_primes`,
    `state`, `earns_moonshine`, and `reason`

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

Concrete file-level shape split for the current checked-in corpus:

- Positive shape (40 files): `ActionMonotonicity.agda`, `AntiFascistSystem.agda`,
  `Base369.agda`, `CRTPeriod.agda`, `Contraction.agda`,
  `CounterexampleHarness.agda`, `DA51Tag.agda`, `DA51Trace.agda`,
  `DASHI_Tests.agda`, `DaslImport.agda`, `Fascism_Tests.agda`,
  `FascisticSystem.agda`, `FixedPoint.agda`, `HGSA_Fixpoints.agda`,
  `JFixedPoint.agda`, `Layer0.agda`, `Layer1.agda`, `Layer2.agda`,
  `Layer3.agda`, `LogicTlurey.agda`, `MaassRestoration.agda`,
  `MonsterConformance.agda`, `MonsterGroups.agda`, `MonsterOntos.agda`,
  `MonsterSpec.agda`, `MonsterState.agda`, `MonsterTraceCounts.agda`,
  `Moonshine.agda`, `MoonshineEarn.agda`, `Overflow.agda`, `PrimeRoles.agda`,
  `ReflectAll.agda`, `SWAR_Equivalence.agda`, `SelfTrace.agda`,
  `SelfWitness.agda`, `TenfoldBridges.agda`, `ThreeAdic_Attractor.agda`,
  `UFTC_Lattice.agda`, `Ultrametric.agda`, `Z6_RegularInverse.agda`
- Negative exception (1 file): `MonsterVectors.agda`

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

## Boundary Freeze

- Freeze date: `2026-03-27`
- Scope owner: `FRACDASH`, using `da51_shards` + `PerfHistory.agda` as the
  canonical input for below-shard codec/modeling claims.
