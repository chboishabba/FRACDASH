# Monster 10-Walk Canonical Semantics

This file freezes the FRACDASH-side canonical semantics for the Monster 10-walk reproduction lane.

Status labels:

- `implemented`: executable + artifact-backed in FRACDASH
- `observed experimentally`: measured from artifacts but not formal proof
- `conjectured`: hypothesis only

## Canonical vertex set (`implemented`)

Use the 10 constants parsed from `monster/MonsterLean/BottPeriodicity.lean`:

`8080, 1742, 479, 451, 2875, 8864, 5990, 496, 1710, 7570`

These are indexed by `position` order from the Lean constants (`0..9`).

## Canonical edge semantics (`implemented`)

Canonical 10-walk edges are the strict position-sequence edges:

`0->1->2->3->4->5->6->7->8->9`

No periodic back-links and no auxiliary clue edges are included in canonical lock mode.
The canonical edge set is now additionally required to be transition-witnessed by FRACDASH physics templates.

Reason:

- This remains the minimal deterministic edge policy that reproduces the observed chain-4 signal under the discussed degeneracy table.
- Witness support is required so lock mode depends on transition data, not sequence policy alone.
- It avoids adding extra policy edges that can inflate chain height.

## Independent FRACDASH re-derivation (`implemented`)

Independent path graphs are derived from FRACDASH transition data (`rank4-dataset` canonical derivation adjacency) for each required template set (currently `physics8`, `physics9`) by:

1. taking the 10-node transition-derived directed graph,
2. solving for a maximum-support Hamiltonian path over those 10 nodes,
3. projecting consecutive path pairs into a 9-edge path graph.

This yields an unlabeled 10-node path candidate from FRACDASH data alone for each template set.

## Match rule between derivations (`implemented`)

Lean-constants canonical graph and each FRACDASH-derived graph are considered matched iff:

- both are directed 10-node path graphs (9 edges, indegree/outdegree path profile),
- each derived undirected path-edge set matches the canonical undirected adjacency pairs `{0-1, 1-2, ..., 8-9}`.

## Lock gate (`implemented`)

Lock passes only if all are true:

1. canonical graph has 10 vertices and 9 edges,
2. canonical graph longest strict descending chain under the observed degeneracy table is exactly `4`,
3. each required template set (`physics8`, `physics9`) yields a valid 10-node path derivation,
4. each required template set provides full (`9/9`) canonical adjacency witness support in direct and reachability transition relations,
5. derivations match canonical adjacency.

## Regression gate (`implemented`)

Run:

`python3 scripts/freeze_monster10walk_canonical.py --strict-lock`

Default lock mode now enforces required template sets `physics8,physics9`.
Use `--template-set <name>` only for one-off legacy checks.

## Claim boundary (`implemented`)

- Passing this lock is an executable FRACDASH reproduction claim for the canonical 10-walk model.
- It is not a full Lean theorem closure claim.
- Lean files with `sorry`/`axiom` remain quarantined until closed.
