module formalism.Physics19StepDelta where

open import Agda.Builtin.Equality using (_≡_; refl)
import formalism.GenericMacroBridge as G
import formalism.Physics15StepDelta as P15

------------------------------------------------------------------------
-- Concrete StepDelta instance for the widened `physics19` bridge slice.
--
-- Keep the widened slice small:
-- - reuse the physics15 IR, normalization, and paired-prime target
-- - add only the source-step constructors and deltas that changed
------------------------------------------------------------------------

open G using (d0; dm1; dm2; dp1; dp2)

Physics19State = P15.Physics15State
Exp6 = P15.Exp6
Delta6 = P15.Delta6

compile : Physics19State → Exp6
compile = P15.compile

infix 20 _↦₁₉_

data _↦₁₉_ : Physics19State → Physics19State → Set where
  physics4-scan-left-high :
    P15.st G.negative G.zero G.zero G.positive G.zero G.negative ↦₁₉
    P15.st G.negative G.zero G.zero G.positive G.positive G.negative

  physics4-scan-left-mid :
    P15.st G.positive G.zero G.zero G.positive G.zero G.negative ↦₁₉
    P15.st G.positive G.zero G.zero G.positive G.positive G.negative

  physics4-scan-right-high :
    P15.st G.zero G.negative G.zero G.positive G.zero G.negative ↦₁₉
    P15.st G.zero G.negative G.zero G.positive G.negative G.negative

  physics4-scan-right-mid :
    P15.st G.zero G.positive G.zero G.positive G.zero G.negative ↦₁₉
    P15.st G.zero G.positive G.zero G.positive G.negative G.negative

  physics2-join-left-high :
    P15.st G.negative G.zero G.zero G.zero G.positive G.negative ↦₁₉
    P15.st G.negative G.zero G.negative G.zero G.positive G.negative

  physics2-join-right-high :
    P15.st G.zero G.negative G.zero G.zero G.negative G.negative ↦₁₉
    P15.st G.zero G.negative G.negative G.zero G.negative G.negative

  physics2-join-left-mid :
    P15.st G.positive G.zero G.zero G.zero G.positive G.negative ↦₁₉
    P15.st G.positive G.zero G.positive G.zero G.positive G.positive

  physics2-join-right-mid :
    P15.st G.zero G.positive G.zero G.zero G.negative G.negative ↦₁₉
    P15.st G.zero G.positive G.positive G.zero G.negative G.positive

  physics2-contract-high :
    P15.st G.zero G.zero G.negative G.positive G.zero G.negative ↦₁₉
    P15.st G.zero G.zero G.positive G.positive G.zero G.positive

  physics2-contract-mid :
    P15.st G.zero G.zero G.positive G.positive G.zero G.positive ↦₁₉
    P15.st G.zero G.zero G.zero G.negative G.zero G.zero

  physics11-boundary-discharge :
    P15.st G.zero G.zero G.zero G.negative G.zero G.negative ↦₁₉
    P15.st G.zero G.zero G.zero G.negative G.zero G.zero

  physics5-boundary-to-shell :
    P15.st G.zero G.zero G.zero G.negative G.zero G.zero ↦₁₉
    P15.st G.zero G.zero G.zero G.zero G.zero G.zero

  physics9-shell-probe-left-high :
    P15.st G.negative G.zero G.zero G.zero G.zero G.zero ↦₁₉
    P15.st G.negative G.zero G.positive G.zero G.positive G.zero

  physics9-shell-probe-right-high :
    P15.st G.zero G.negative G.zero G.zero G.zero G.zero ↦₁₉
    P15.st G.zero G.negative G.positive G.zero G.negative G.zero

  physics9-shell-probe-left-mid :
    P15.st G.positive G.zero G.zero G.zero G.zero G.zero ↦₁₉
    P15.st G.positive G.zero G.positive G.zero G.positive G.zero

  physics9-shell-probe-right-mid :
    P15.st G.zero G.positive G.zero G.zero G.zero G.zero ↦₁₉
    P15.st G.zero G.positive G.positive G.zero G.negative G.zero

  physics9-shell-stage-release-left :
    P15.st G.zero G.zero G.positive G.zero G.positive G.zero ↦₁₉
    P15.st G.zero G.zero G.zero G.zero G.positive G.zero

  physics12-shell-stage-detour-left :
    P15.st G.zero G.zero G.positive G.zero G.positive G.zero ↦₁₉
    P15.st G.zero G.zero G.zero G.negative G.positive G.zero

  physics12-shell-stage-detour-right :
    P15.st G.zero G.zero G.positive G.zero G.negative G.zero ↦₁₉
    P15.st G.zero G.zero G.zero G.negative G.negative G.zero

  physics9-shell-stage-release-right :
    P15.st G.zero G.zero G.positive G.zero G.negative G.zero ↦₁₉
    P15.st G.zero G.zero G.zero G.zero G.negative G.zero

  physics10-shell-probe-neutral :
    P15.st G.zero G.zero G.zero G.zero G.zero G.zero ↦₁₉
    P15.st G.zero G.zero G.positive G.zero G.positive G.zero

  physics6-shell-refresh-left :
    P15.st G.zero G.zero G.zero G.zero G.positive G.zero ↦₁₉
    P15.st G.zero G.zero G.zero G.zero G.zero G.zero

  physics6-shell-refresh-right :
    P15.st G.zero G.zero G.zero G.zero G.negative G.zero ↦₁₉
    P15.st G.zero G.zero G.zero G.zero G.zero G.zero

  physics5-shell-to-interior-cleared :
    P15.st G.zero G.zero G.zero G.zero G.zero G.zero ↦₁₉
    P15.st G.zero G.zero G.zero G.positive G.zero G.negative

  physics5-shell-to-interior-latched-left :
    P15.st G.zero G.zero G.zero G.zero G.positive G.zero ↦₁₉
    P15.st G.zero G.zero G.zero G.positive G.positive G.negative

  physics5-shell-to-interior-latched-right :
    P15.st G.zero G.zero G.zero G.zero G.negative G.zero ↦₁₉
    P15.st G.zero G.zero G.zero G.positive G.negative G.negative

  physics13-contract-mid-detour-nn :
    P15.st G.negative G.negative G.positive G.positive G.negative G.positive ↦₁₉
    P15.st G.negative G.negative G.zero G.negative G.zero G.zero

  physics14-shell-high-rearm :
    P15.st G.zero G.zero G.negative G.zero G.zero G.negative ↦₁₉
    P15.st G.zero G.zero G.negative G.positive G.zero G.negative

  physics15-boundary-crossfeed-neutral :
    P15.st G.negative G.negative G.zero G.negative G.zero G.zero ↦₁₉
    P15.st G.negative G.positive G.zero G.negative G.zero G.zero

  physics16-boundary-discharge-high :
    P15.st G.zero G.zero G.negative G.negative G.zero G.negative ↦₁₉
    P15.st G.zero G.zero G.zero G.negative G.zero G.zero

  physics17-boundary-handoff-left-to-mid :
    P15.st G.negative G.positive G.zero G.negative G.positive G.zero ↦₁₉
    P15.st G.negative G.zero G.zero G.negative G.positive G.zero

  physics18-boundary-discharge-mid :
    P15.st G.zero G.zero G.positive G.negative G.zero G.negative ↦₁₉
    P15.st G.zero G.zero G.zero G.negative G.zero G.zero

  physics19-tail-handoff-n0-to-nn :
    P15.st G.negative G.zero G.positive G.positive G.positive G.positive ↦₁₉
    P15.st G.negative G.negative G.positive G.positive G.positive G.positive

deltaOf : ∀ {x x'} → x ↦₁₉ x' → Delta6
deltaOf physics4-scan-left-high = P15.delta6 d0 d0 d0 d0 dp1 d0
deltaOf physics4-scan-left-mid = P15.delta6 d0 d0 d0 d0 dp1 d0
deltaOf physics4-scan-right-high = P15.delta6 d0 d0 d0 d0 dm1 d0
deltaOf physics4-scan-right-mid = P15.delta6 d0 d0 d0 d0 dm1 d0
deltaOf physics2-join-left-high = P15.delta6 d0 d0 dm1 d0 d0 d0
deltaOf physics2-join-right-high = P15.delta6 d0 d0 dm1 d0 d0 d0
deltaOf physics2-join-left-mid = P15.delta6 d0 d0 dp1 d0 d0 dp2
deltaOf physics2-join-right-mid = P15.delta6 d0 d0 dp1 d0 d0 dp2
deltaOf physics2-contract-high = P15.delta6 d0 d0 dp2 d0 d0 dp2
deltaOf physics2-contract-mid = P15.delta6 d0 d0 dm1 dm2 d0 dm1
deltaOf physics11-boundary-discharge = P15.delta6 d0 d0 d0 d0 d0 dp1
deltaOf physics5-boundary-to-shell = P15.delta6 d0 d0 d0 dp1 d0 d0
deltaOf physics9-shell-probe-left-high = P15.delta6 d0 d0 dp1 d0 dp1 d0
deltaOf physics9-shell-probe-right-high = P15.delta6 d0 d0 dp1 d0 dm1 d0
deltaOf physics9-shell-probe-left-mid = P15.delta6 d0 d0 dp1 d0 dp1 d0
deltaOf physics9-shell-probe-right-mid = P15.delta6 d0 d0 dp1 d0 dm1 d0
deltaOf physics9-shell-stage-release-left = P15.delta6 d0 d0 dm1 d0 d0 d0
deltaOf physics12-shell-stage-detour-left = P15.delta6 d0 d0 dm1 dm1 d0 d0
deltaOf physics12-shell-stage-detour-right = P15.delta6 d0 d0 dm1 dm1 d0 d0
deltaOf physics9-shell-stage-release-right = P15.delta6 d0 d0 dm1 d0 d0 d0
deltaOf physics10-shell-probe-neutral = P15.delta6 d0 d0 dp1 d0 dp1 d0
deltaOf physics6-shell-refresh-left = P15.delta6 d0 d0 d0 d0 dm1 d0
deltaOf physics6-shell-refresh-right = P15.delta6 d0 d0 d0 d0 dp1 d0
deltaOf physics5-shell-to-interior-cleared = P15.delta6 d0 d0 d0 dp1 d0 dm1
deltaOf physics5-shell-to-interior-latched-left = P15.delta6 d0 d0 d0 dp1 d0 dm1
deltaOf physics5-shell-to-interior-latched-right = P15.delta6 d0 d0 d0 dp1 d0 dm1
deltaOf physics13-contract-mid-detour-nn = P15.delta6 d0 d0 dm1 dm2 dp1 dm1
deltaOf physics14-shell-high-rearm = P15.delta6 d0 d0 d0 dp1 d0 d0
deltaOf physics15-boundary-crossfeed-neutral = P15.delta6 d0 dp2 d0 d0 d0 d0
deltaOf physics16-boundary-discharge-high = P15.delta6 d0 d0 dp1 d0 d0 dp1
deltaOf physics17-boundary-handoff-left-to-mid = P15.delta6 d0 dm1 d0 d0 d0 d0
deltaOf physics18-boundary-discharge-mid = P15.delta6 d0 d0 dm1 d0 d0 dp1
deltaOf physics19-tail-handoff-n0-to-nn = P15.delta6 d0 dm1 d0 d0 d0 d0

normalizationContract : G.NormalizationContract P15.irOps
normalizationContract = P15.normalizationContract

primeExecution : G.PrimeExecution P15.irOps
primeExecution = P15.primeExecution

unitRealization : G.UnitRealization P15.irOps primeExecution
unitRealization = P15.unitRealization

realizeNormalized = P15.realizeNormalized

delta-correct : ∀ {x x'} → (sx : x ↦₁₉ x') → compile x' ≡ P15.applyDelta6 (compile x) (deltaOf sx)
delta-correct physics4-scan-left-high = refl
delta-correct physics4-scan-left-mid = refl
delta-correct physics4-scan-right-high = refl
delta-correct physics4-scan-right-mid = refl
delta-correct physics2-join-left-high = refl
delta-correct physics2-join-right-high = refl
delta-correct physics2-join-left-mid = refl
delta-correct physics2-join-right-mid = refl
delta-correct physics2-contract-high = refl
delta-correct physics2-contract-mid = refl
delta-correct physics11-boundary-discharge = refl
delta-correct physics5-boundary-to-shell = refl
delta-correct physics9-shell-probe-left-high = refl
delta-correct physics9-shell-probe-right-high = refl
delta-correct physics9-shell-probe-left-mid = refl
delta-correct physics9-shell-probe-right-mid = refl
delta-correct physics9-shell-stage-release-left = refl
delta-correct physics12-shell-stage-detour-left = refl
delta-correct physics12-shell-stage-detour-right = refl
delta-correct physics9-shell-stage-release-right = refl
delta-correct physics10-shell-probe-neutral = refl
delta-correct physics6-shell-refresh-left = refl
delta-correct physics6-shell-refresh-right = refl
delta-correct physics5-shell-to-interior-cleared = refl
delta-correct physics5-shell-to-interior-latched-left = refl
delta-correct physics5-shell-to-interior-latched-right = refl
delta-correct physics13-contract-mid-detour-nn = refl
delta-correct physics14-shell-high-rearm = refl
delta-correct physics15-boundary-crossfeed-neutral = refl
delta-correct physics16-boundary-discharge-high = refl
delta-correct physics17-boundary-handoff-left-to-mid = refl
delta-correct physics18-boundary-discharge-mid = refl
delta-correct physics19-tail-handoff-n0-to-nn = refl

normalize-correct :
  ∀ {x x'} →
  (sx : x ↦₁₉ x') →
  compile x' ≡ G.applyUnitDeltas P15.irOps (compile x) (G.normalize P15.irOps (deltaOf sx))
normalize-correct physics4-scan-left-high = refl
normalize-correct physics4-scan-left-mid = refl
normalize-correct physics4-scan-right-high = refl
normalize-correct physics4-scan-right-mid = refl
normalize-correct physics2-join-left-high = refl
normalize-correct physics2-join-right-high = refl
normalize-correct physics2-join-left-mid = refl
normalize-correct physics2-join-right-mid = refl
normalize-correct physics2-contract-high = refl
normalize-correct physics2-contract-mid = refl
normalize-correct physics11-boundary-discharge = refl
normalize-correct physics5-boundary-to-shell = refl
normalize-correct physics9-shell-probe-left-high = refl
normalize-correct physics9-shell-probe-right-high = refl
normalize-correct physics9-shell-probe-left-mid = refl
normalize-correct physics9-shell-probe-right-mid = refl
normalize-correct physics9-shell-stage-release-left = refl
normalize-correct physics12-shell-stage-detour-left = refl
normalize-correct physics12-shell-stage-detour-right = refl
normalize-correct physics9-shell-stage-release-right = refl
normalize-correct physics10-shell-probe-neutral = refl
normalize-correct physics6-shell-refresh-left = refl
normalize-correct physics6-shell-refresh-right = refl
normalize-correct physics5-shell-to-interior-cleared = refl
normalize-correct physics5-shell-to-interior-latched-left = refl
normalize-correct physics5-shell-to-interior-latched-right = refl
normalize-correct physics13-contract-mid-detour-nn = refl
normalize-correct physics14-shell-high-rearm = refl
normalize-correct physics15-boundary-crossfeed-neutral = refl
normalize-correct physics16-boundary-discharge-high = refl
normalize-correct physics17-boundary-handoff-left-to-mid = refl
normalize-correct physics18-boundary-discharge-mid = refl
normalize-correct physics19-tail-handoff-n0-to-nn = refl

realizeNormalized-target-sound :
  ∀ {x x'} →
  (sx : x ↦₁₉ x') →
  compile x' ≡
    P15.decodeY
      (G.applyFracs primeExecution
        (P15.encodeY (compile x))
        (realizeNormalized (compile x) (G.normalize P15.irOps (deltaOf sx))))
realizeNormalized-target-sound {x = x} sx =
  G.trans
    (delta-correct sx)
    (G.sym (G.realizeDelta-sound normalizationContract primeExecution unitRealization (compile x) (deltaOf sx)))

data RegimeClass : Set where
  conservative-contracting : RegimeClass
  transmuting-contracting : RegimeClass

ruleClass : ∀ {x x'} → x ↦₁₉ x' → RegimeClass
ruleClass physics4-scan-left-high = conservative-contracting
ruleClass physics4-scan-left-mid = conservative-contracting
ruleClass physics4-scan-right-high = conservative-contracting
ruleClass physics4-scan-right-mid = conservative-contracting
ruleClass physics2-join-left-high = conservative-contracting
ruleClass physics2-join-right-high = conservative-contracting
ruleClass physics2-join-left-mid = conservative-contracting
ruleClass physics2-join-right-mid = conservative-contracting
ruleClass physics2-contract-high = conservative-contracting
ruleClass physics2-contract-mid = conservative-contracting
ruleClass physics11-boundary-discharge = conservative-contracting
ruleClass physics5-boundary-to-shell = conservative-contracting
ruleClass physics9-shell-probe-left-high = conservative-contracting
ruleClass physics9-shell-probe-right-high = conservative-contracting
ruleClass physics9-shell-probe-left-mid = conservative-contracting
ruleClass physics9-shell-probe-right-mid = conservative-contracting
ruleClass physics9-shell-stage-release-left = conservative-contracting
ruleClass physics12-shell-stage-detour-left = conservative-contracting
ruleClass physics12-shell-stage-detour-right = conservative-contracting
ruleClass physics9-shell-stage-release-right = conservative-contracting
ruleClass physics10-shell-probe-neutral = conservative-contracting
ruleClass physics6-shell-refresh-left = conservative-contracting
ruleClass physics6-shell-refresh-right = conservative-contracting
ruleClass physics5-shell-to-interior-cleared = conservative-contracting
ruleClass physics5-shell-to-interior-latched-left = conservative-contracting
ruleClass physics5-shell-to-interior-latched-right = conservative-contracting
ruleClass physics13-contract-mid-detour-nn = conservative-contracting
ruleClass physics14-shell-high-rearm = conservative-contracting
ruleClass physics15-boundary-crossfeed-neutral = transmuting-contracting
ruleClass physics16-boundary-discharge-high = conservative-contracting
ruleClass physics17-boundary-handoff-left-to-mid = transmuting-contracting
ruleClass physics18-boundary-discharge-mid = conservative-contracting
ruleClass physics19-tail-handoff-n0-to-nn = transmuting-contracting

data StrictlyContracting : Set where
  strictly-contracting : StrictlyContracting

data BoundedTransmutation : RegimeClass → Set where
  conservative-bound : BoundedTransmutation conservative-contracting
  transmuting-bound : BoundedTransmutation transmuting-contracting

record RegimeWitness {x x'} (sx : x ↦₁₉ x') : Set where
  constructor regime-witness
  field
    class : RegimeClass
    contracting : StrictlyContracting
    transmutation : BoundedTransmutation class
    wellFormed-target :
      P15.WellFormedPrimeState6
        (G.applyFracs primeExecution
          (P15.encodeY (compile x))
          (realizeNormalized (compile x) (G.normalize P15.irOps (deltaOf sx))))

physics19-regime-valid : ∀ {x x'} (sx : x ↦₁₉ x') → RegimeWitness sx
physics19-regime-valid {x = x} physics4-scan-left-high =
  regime-witness conservative-contracting strictly-contracting conservative-bound
    (G.realizeDelta-preserves-wellFormed primeExecution unitRealization (compile x) (deltaOf physics4-scan-left-high))
physics19-regime-valid {x = x} physics4-scan-left-mid =
  regime-witness conservative-contracting strictly-contracting conservative-bound
    (G.realizeDelta-preserves-wellFormed primeExecution unitRealization (compile x) (deltaOf physics4-scan-left-mid))
physics19-regime-valid {x = x} physics4-scan-right-high =
  regime-witness conservative-contracting strictly-contracting conservative-bound
    (G.realizeDelta-preserves-wellFormed primeExecution unitRealization (compile x) (deltaOf physics4-scan-right-high))
physics19-regime-valid {x = x} physics4-scan-right-mid =
  regime-witness conservative-contracting strictly-contracting conservative-bound
    (G.realizeDelta-preserves-wellFormed primeExecution unitRealization (compile x) (deltaOf physics4-scan-right-mid))
physics19-regime-valid {x = x} physics2-join-left-high =
  regime-witness conservative-contracting strictly-contracting conservative-bound
    (G.realizeDelta-preserves-wellFormed primeExecution unitRealization (compile x) (deltaOf physics2-join-left-high))
physics19-regime-valid {x = x} physics2-join-right-high =
  regime-witness conservative-contracting strictly-contracting conservative-bound
    (G.realizeDelta-preserves-wellFormed primeExecution unitRealization (compile x) (deltaOf physics2-join-right-high))
physics19-regime-valid {x = x} physics2-join-left-mid =
  regime-witness conservative-contracting strictly-contracting conservative-bound
    (G.realizeDelta-preserves-wellFormed primeExecution unitRealization (compile x) (deltaOf physics2-join-left-mid))
physics19-regime-valid {x = x} physics2-join-right-mid =
  regime-witness conservative-contracting strictly-contracting conservative-bound
    (G.realizeDelta-preserves-wellFormed primeExecution unitRealization (compile x) (deltaOf physics2-join-right-mid))
physics19-regime-valid {x = x} physics2-contract-high =
  regime-witness conservative-contracting strictly-contracting conservative-bound
    (G.realizeDelta-preserves-wellFormed primeExecution unitRealization (compile x) (deltaOf physics2-contract-high))
physics19-regime-valid {x = x} physics2-contract-mid =
  regime-witness conservative-contracting strictly-contracting conservative-bound
    (G.realizeDelta-preserves-wellFormed primeExecution unitRealization (compile x) (deltaOf physics2-contract-mid))
physics19-regime-valid {x = x} physics11-boundary-discharge =
  regime-witness conservative-contracting strictly-contracting conservative-bound
    (G.realizeDelta-preserves-wellFormed primeExecution unitRealization (compile x) (deltaOf physics11-boundary-discharge))
physics19-regime-valid {x = x} physics5-boundary-to-shell =
  regime-witness conservative-contracting strictly-contracting conservative-bound
    (G.realizeDelta-preserves-wellFormed primeExecution unitRealization (compile x) (deltaOf physics5-boundary-to-shell))
physics19-regime-valid {x = x} physics9-shell-probe-left-high =
  regime-witness conservative-contracting strictly-contracting conservative-bound
    (G.realizeDelta-preserves-wellFormed primeExecution unitRealization (compile x) (deltaOf physics9-shell-probe-left-high))
physics19-regime-valid {x = x} physics9-shell-probe-right-high =
  regime-witness conservative-contracting strictly-contracting conservative-bound
    (G.realizeDelta-preserves-wellFormed primeExecution unitRealization (compile x) (deltaOf physics9-shell-probe-right-high))
physics19-regime-valid {x = x} physics9-shell-probe-left-mid =
  regime-witness conservative-contracting strictly-contracting conservative-bound
    (G.realizeDelta-preserves-wellFormed primeExecution unitRealization (compile x) (deltaOf physics9-shell-probe-left-mid))
physics19-regime-valid {x = x} physics9-shell-probe-right-mid =
  regime-witness conservative-contracting strictly-contracting conservative-bound
    (G.realizeDelta-preserves-wellFormed primeExecution unitRealization (compile x) (deltaOf physics9-shell-probe-right-mid))
physics19-regime-valid {x = x} physics9-shell-stage-release-left =
  regime-witness conservative-contracting strictly-contracting conservative-bound
    (G.realizeDelta-preserves-wellFormed primeExecution unitRealization (compile x) (deltaOf physics9-shell-stage-release-left))
physics19-regime-valid {x = x} physics12-shell-stage-detour-left =
  regime-witness conservative-contracting strictly-contracting conservative-bound
    (G.realizeDelta-preserves-wellFormed primeExecution unitRealization (compile x) (deltaOf physics12-shell-stage-detour-left))
physics19-regime-valid {x = x} physics12-shell-stage-detour-right =
  regime-witness conservative-contracting strictly-contracting conservative-bound
    (G.realizeDelta-preserves-wellFormed primeExecution unitRealization (compile x) (deltaOf physics12-shell-stage-detour-right))
physics19-regime-valid {x = x} physics9-shell-stage-release-right =
  regime-witness conservative-contracting strictly-contracting conservative-bound
    (G.realizeDelta-preserves-wellFormed primeExecution unitRealization (compile x) (deltaOf physics9-shell-stage-release-right))
physics19-regime-valid {x = x} physics10-shell-probe-neutral =
  regime-witness conservative-contracting strictly-contracting conservative-bound
    (G.realizeDelta-preserves-wellFormed primeExecution unitRealization (compile x) (deltaOf physics10-shell-probe-neutral))
physics19-regime-valid {x = x} physics6-shell-refresh-left =
  regime-witness conservative-contracting strictly-contracting conservative-bound
    (G.realizeDelta-preserves-wellFormed primeExecution unitRealization (compile x) (deltaOf physics6-shell-refresh-left))
physics19-regime-valid {x = x} physics6-shell-refresh-right =
  regime-witness conservative-contracting strictly-contracting conservative-bound
    (G.realizeDelta-preserves-wellFormed primeExecution unitRealization (compile x) (deltaOf physics6-shell-refresh-right))
physics19-regime-valid {x = x} physics5-shell-to-interior-cleared =
  regime-witness conservative-contracting strictly-contracting conservative-bound
    (G.realizeDelta-preserves-wellFormed primeExecution unitRealization (compile x) (deltaOf physics5-shell-to-interior-cleared))
physics19-regime-valid {x = x} physics5-shell-to-interior-latched-left =
  regime-witness conservative-contracting strictly-contracting conservative-bound
    (G.realizeDelta-preserves-wellFormed primeExecution unitRealization (compile x) (deltaOf physics5-shell-to-interior-latched-left))
physics19-regime-valid {x = x} physics5-shell-to-interior-latched-right =
  regime-witness conservative-contracting strictly-contracting conservative-bound
    (G.realizeDelta-preserves-wellFormed primeExecution unitRealization (compile x) (deltaOf physics5-shell-to-interior-latched-right))
physics19-regime-valid {x = x} physics13-contract-mid-detour-nn =
  regime-witness conservative-contracting strictly-contracting conservative-bound
    (G.realizeDelta-preserves-wellFormed primeExecution unitRealization (compile x) (deltaOf physics13-contract-mid-detour-nn))
physics19-regime-valid {x = x} physics14-shell-high-rearm =
  regime-witness conservative-contracting strictly-contracting conservative-bound
    (G.realizeDelta-preserves-wellFormed primeExecution unitRealization (compile x) (deltaOf physics14-shell-high-rearm))
physics19-regime-valid {x = x} physics15-boundary-crossfeed-neutral =
  regime-witness transmuting-contracting strictly-contracting transmuting-bound
    (G.realizeDelta-preserves-wellFormed primeExecution unitRealization (compile x) (deltaOf physics15-boundary-crossfeed-neutral))
physics19-regime-valid {x = x} physics16-boundary-discharge-high =
  regime-witness conservative-contracting strictly-contracting conservative-bound
    (G.realizeDelta-preserves-wellFormed primeExecution unitRealization (compile x) (deltaOf physics16-boundary-discharge-high))
physics19-regime-valid {x = x} physics17-boundary-handoff-left-to-mid =
  regime-witness transmuting-contracting strictly-contracting transmuting-bound
    (G.realizeDelta-preserves-wellFormed primeExecution unitRealization (compile x) (deltaOf physics17-boundary-handoff-left-to-mid))
physics19-regime-valid {x = x} physics18-boundary-discharge-mid =
  regime-witness conservative-contracting strictly-contracting conservative-bound
    (G.realizeDelta-preserves-wellFormed primeExecution unitRealization (compile x) (deltaOf physics18-boundary-discharge-mid))
physics19-regime-valid {x = x} physics19-tail-handoff-n0-to-nn =
  regime-witness transmuting-contracting strictly-contracting transmuting-bound
    (G.realizeDelta-preserves-wellFormed primeExecution unitRealization (compile x) (deltaOf physics19-tail-handoff-n0-to-nn))
