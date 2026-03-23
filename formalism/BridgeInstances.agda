module formalism.BridgeInstances where

open import Agda.Builtin.Equality using (_≡_; refl)
open import Agda.Builtin.Sigma using (Σ; _,_; fst; snd)
open import Agda.Builtin.Nat using (Nat; zero; suc)
open import Agda.Builtin.Unit using (⊤; tt)

import formalism.GenericMacroBridge as G
import formalism.Physics1StepDelta as P1
import formalism.Physics3StepDelta as P3
import formalism.Physics15StepDelta as P15
import formalism.Physics19StepDelta as P19
import formalism.Physics20StepDelta as P20
import formalism.Physics21StepDelta as P21
import formalism.Physics22StepDelta as P22
import formalism.ExecutionWitnessSketch as EW

------------------------------------------------------------------------
-- Thin master instantiation layer for the current closed bridge slices.
--
-- Keep the concrete slice files separate:
-- - Physics1StepDelta.agda
-- - Physics3StepDelta.agda
-- - Physics15StepDelta.agda
--
-- This file exists only to state the current bridge theorem surface once.
------------------------------------------------------------------------

physics1-classify :
  P1.Exp4 → P1.Delta4 → G.RegimeClass
physics1-classify y δ = G.conservative-contracting

physics3-classify :
  P3.Exp6 → P3.Delta6 → G.RegimeClass
physics3-classify y δ = G.conservative-contracting

physics15-classify :
  P15.Exp6 → P15.Delta6 → G.RegimeClass
physics15-classify y (P15.delta6 G.d0 G.dp2 G.d0 G.d0 G.d0 G.d0) = G.transmuting-contracting
physics15-classify y δ = G.conservative-contracting

physics19-classify :
  P19.Exp6 → P19.Delta6 → G.RegimeClass
physics19-classify y (P15.delta6 G.d0 G.dp2 G.d0 G.d0 G.d0 G.d0) = G.transmuting-contracting
physics19-classify y (P15.delta6 G.d0 G.dm1 G.d0 G.d0 G.d0 G.d0) = G.transmuting-contracting
physics19-classify y δ = G.conservative-contracting

physics20-classify :
  P20.Exp6 → P20.Delta6 → G.RegimeClass
physics20-classify y (P15.delta6 G.d0 G.dp2 G.d0 G.d0 G.d0 G.d0) = G.transmuting-contracting
physics20-classify y (P15.delta6 G.d0 G.dm1 G.d0 G.d0 G.d0 G.d0) = G.transmuting-contracting
physics20-classify y δ = G.conservative-contracting

physics21-classify :
  P21.Exp6 → P21.Delta6 → G.RegimeClass
physics21-classify y (P15.delta6 G.d0 G.dp2 G.d0 G.d0 G.d0 G.d0) = G.transmuting-contracting
physics21-classify y (P15.delta6 G.d0 G.dm1 G.d0 G.d0 G.d0 G.d0) = G.transmuting-contracting
physics21-classify y δ = G.conservative-contracting

physics22-classify :
  P22.Exp6 → P22.Delta6 → G.RegimeClass
physics22-classify y (P15.delta6 G.d0 G.dp2 G.d0 G.d0 G.d0 G.d0) = G.transmuting-contracting
physics22-classify y (P15.delta6 G.d0 G.dm1 G.d0 G.d0 G.d0 G.d0) = G.transmuting-contracting
physics22-classify y δ = G.conservative-contracting

physics15-strict-contraction :
  ∀ y δ →
  G.StrictContractionWitness (physics15-classify y δ)
physics15-strict-contraction y δ with physics15-classify y δ
... | G.conservative-contracting = G.conservative-strict
... | G.transmuting-contracting = G.transmuting-strict

physics15-bounded-transmutation :
  ∀ y δ →
  G.BoundedTransmutationWitness (physics15-classify y δ)
physics15-bounded-transmutation y δ with physics15-classify y δ
... | G.conservative-contracting = G.zero-transmutation
... | G.transmuting-contracting = G.bounded-transmutation-witness

physics19-strict-contraction :
  ∀ y δ →
  G.StrictContractionWitness (physics19-classify y δ)
physics19-strict-contraction y δ with physics19-classify y δ
... | G.conservative-contracting = G.conservative-strict
... | G.transmuting-contracting = G.transmuting-strict

physics19-bounded-transmutation :
  ∀ y δ →
  G.BoundedTransmutationWitness (physics19-classify y δ)
physics19-bounded-transmutation y δ with physics19-classify y δ
... | G.conservative-contracting = G.zero-transmutation
... | G.transmuting-contracting = G.bounded-transmutation-witness

physics20-strict-contraction :
  ∀ y δ →
  G.StrictContractionWitness (physics20-classify y δ)
physics20-strict-contraction y δ with physics20-classify y δ
... | G.conservative-contracting = G.conservative-strict
... | G.transmuting-contracting = G.transmuting-strict

physics20-bounded-transmutation :
  ∀ y δ →
  G.BoundedTransmutationWitness (physics20-classify y δ)
physics20-bounded-transmutation y δ with physics20-classify y δ
... | G.conservative-contracting = G.zero-transmutation
... | G.transmuting-contracting = G.bounded-transmutation-witness

physics21-strict-contraction :
  ∀ y δ →
  G.StrictContractionWitness (physics21-classify y δ)
physics21-strict-contraction y δ with physics21-classify y δ
... | G.conservative-contracting = G.conservative-strict
... | G.transmuting-contracting = G.transmuting-strict

physics21-bounded-transmutation :
  ∀ y δ →
  G.BoundedTransmutationWitness (physics21-classify y δ)
physics21-bounded-transmutation y δ with physics21-classify y δ
... | G.conservative-contracting = G.zero-transmutation
... | G.transmuting-contracting = G.bounded-transmutation-witness

physics22-strict-contraction :
  ∀ y δ →
  G.StrictContractionWitness (physics22-classify y δ)
physics22-strict-contraction y δ with physics22-classify y δ
... | G.conservative-contracting = G.conservative-strict
... | G.transmuting-contracting = G.transmuting-strict

physics22-bounded-transmutation :
  ∀ y δ →
  G.BoundedTransmutationWitness (physics22-classify y δ)
physics22-bounded-transmutation y δ with physics22-classify y δ
... | G.conservative-contracting = G.zero-transmutation
... | G.transmuting-contracting = G.bounded-transmutation-witness

------------------------------------------------------------------------
-- Executable witness/status surfaces (stubbed except physics15).
------------------------------------------------------------------------

physics1-execution-admissible :
  P1.Exp4 → P1.Delta4 → Set
physics1-execution-admissible y δ =
  G.WellFormedY P1.primeExecution
    (G.applyFracs P1.primeExecution
      (P1.encodeY y)
      (G.realizeNormalized P1.primeExecution P1.unitRealization y (P1.normalize δ)))

physics1-execution-evidence :
  ∀ y δ → physics1-execution-admissible y δ
physics1-execution-evidence y δ =
  G.realizeDelta-preserves-wellFormed P1.primeExecution P1.unitRealization y δ

status1 : EW.ExecutionStatus (G.PrimeExecution.PrimeState P1.primeExecution)
status1 = record
  { regimeClass = G.conservative-contracting
  ; wellFormedY = G.PrimeExecution.WellFormedY P1.primeExecution
  ; executionAdmissible = ∀ y δ → physics1-execution-admissible y δ
  ; familyTag = G.RegimeClass
  ; evidence = physics1-execution-evidence
  }

physics3-execution-admissible :
  P3.Exp6 → P3.Delta6 → Set
physics3-execution-admissible y δ =
  G.WellFormedY P3.primeExecution
    (G.applyFracs P3.primeExecution
      (P3.encodeY y)
      (G.realizeNormalized P3.primeExecution P3.unitRealization y (P3.normalize δ)))

physics3-execution-evidence :
  ∀ y δ → physics3-execution-admissible y δ
physics3-execution-evidence y δ =
  G.realizeDelta-preserves-wellFormed P3.primeExecution P3.unitRealization y δ

status3 : EW.ExecutionStatus (G.PrimeExecution.PrimeState P3.primeExecution)
status3 = record
  { regimeClass = G.conservative-contracting
  ; wellFormedY = G.PrimeExecution.WellFormedY P3.primeExecution
  ; executionAdmissible = ∀ y δ → physics3-execution-admissible y δ
  ; familyTag = G.RegimeClass
  ; evidence = physics3-execution-evidence
  }

physics15-execution-admissible :
  P15.Exp6 → P15.Delta6 → Set
physics15-execution-admissible y δ =
  G.WellFormedY P15.primeExecution
    (G.applyFracs P15.primeExecution
      (P15.encodeY y)
      (G.realizeNormalized P15.primeExecution P15.unitRealization y (P15.normalize δ)))

physics15-execution-evidence :
  ∀ y δ → physics15-execution-admissible y δ
physics15-execution-evidence y δ =
  G.realizeDelta-preserves-wellFormed P15.primeExecution P15.unitRealization y δ

status15 : EW.ExecutionStatus (G.PrimeExecution.PrimeState P15.primeExecution)
status15 = record
  { regimeClass = G.conservative-contracting
  ; wellFormedY = G.PrimeExecution.WellFormedY P15.primeExecution
  ; executionAdmissible = ∀ y δ → physics15-execution-admissible y δ
  ; familyTag = G.RegimeClass
  ; evidence = physics15-execution-evidence
  }

physics19-execution-admissible :
  P19.Exp6 → P19.Delta6 → Set
physics19-execution-admissible y δ =
  G.WellFormedY P19.primeExecution
    (G.applyFracs P19.primeExecution
      (P19.encodeY y)
      (G.realizeNormalized P19.primeExecution P19.unitRealization y (P19.normalize δ)))

physics19-execution-evidence :
  ∀ y δ → physics19-execution-admissible y δ
physics19-execution-evidence y δ =
  G.realizeDelta-preserves-wellFormed P19.primeExecution P19.unitRealization y δ

status19 : EW.ExecutionStatus (G.PrimeExecution.PrimeState P19.primeExecution)
status19 = record
  { regimeClass = G.conservative-contracting
  ; wellFormedY = G.PrimeExecution.WellFormedY P19.primeExecution
  ; executionAdmissible = ∀ y δ → physics19-execution-admissible y δ
  ; familyTag = G.RegimeClass
  ; evidence = physics19-execution-evidence
  }

physics20-execution-admissible :
  P20.Exp6 → P20.Delta6 → Set
physics20-execution-admissible y δ =
  G.WellFormedY P20.primeExecution
    (G.applyFracs P20.primeExecution
      (P20.encodeY y)
      (G.realizeNormalized P20.primeExecution P20.unitRealization y (P20.normalize δ)))

physics20-execution-evidence :
  ∀ y δ → physics20-execution-admissible y δ
physics20-execution-evidence y δ =
  G.realizeDelta-preserves-wellFormed P20.primeExecution P20.unitRealization y δ

status20 : EW.ExecutionStatus (G.PrimeExecution.PrimeState P20.primeExecution)
status20 = record
  { regimeClass = G.conservative-contracting
  ; wellFormedY = G.PrimeExecution.WellFormedY P20.primeExecution
  ; executionAdmissible = ∀ y δ → physics20-execution-admissible y δ
  ; familyTag = G.RegimeClass
  ; evidence = physics20-execution-evidence
  }

physics21-execution-admissible :
  P21.Exp6 → P21.Delta6 → Set
physics21-execution-admissible y δ =
  G.WellFormedY P21.primeExecution
    (G.applyFracs P21.primeExecution
      (P21.encodeY y)
      (G.realizeNormalized P21.primeExecution P21.unitRealization y (P21.normalize δ)))

physics21-execution-evidence :
  ∀ y δ → physics21-execution-admissible y δ
physics21-execution-evidence y δ =
  G.realizeDelta-preserves-wellFormed P21.primeExecution P21.unitRealization y δ

status21 : EW.ExecutionStatus (G.PrimeExecution.PrimeState P21.primeExecution)
status21 = record
  { regimeClass = G.conservative-contracting
  ; wellFormedY = G.PrimeExecution.WellFormedY P21.primeExecution
  ; executionAdmissible = ∀ y δ → physics21-execution-admissible y δ
  ; familyTag = G.RegimeClass
  ; evidence = physics21-execution-evidence
  }

physics22-execution-admissible :
  P22.Exp6 → P22.Delta6 → Set
physics22-execution-admissible y δ =
  G.WellFormedY P22.primeExecution
    (G.applyFracs P22.primeExecution
      (P22.encodeY y)
      (G.realizeNormalized P22.primeExecution P22.unitRealization y (P22.normalize δ)))

physics22-execution-evidence :
  ∀ y δ → physics22-execution-admissible y δ
physics22-execution-evidence y δ =
  G.realizeDelta-preserves-wellFormed P22.primeExecution P22.unitRealization y δ

status22 : EW.ExecutionStatus (G.PrimeExecution.PrimeState P22.primeExecution)
status22 = record
  { regimeClass = G.conservative-contracting
  ; wellFormedY = G.PrimeExecution.WellFormedY P22.primeExecution
  ; executionAdmissible = ∀ y δ → physics22-execution-admissible y δ
  ; familyTag = G.RegimeClass
  ; evidence = physics22-execution-evidence
  }

physics1-bridge : G.RegimeValidBridge P1.normalizationContract P1.primeExecution P1.unitRealization
physics1-bridge = record
  { classifyDelta = physics1-classify
  ; wellFormed-preserved = G.default-wellFormed-preserved P1.primeExecution P1.unitRealization
  ; strict-contraction = λ y δ → G.conservative-strict
  ; bounded-transmutation = λ y δ → G.zero-transmutation
  }

physics3-bridge : G.RegimeValidBridge P3.normalizationContract P3.primeExecution P3.unitRealization
physics3-bridge = record
  { classifyDelta = physics3-classify
  ; wellFormed-preserved = G.default-wellFormed-preserved P3.primeExecution P3.unitRealization
  ; strict-contraction = λ y δ → G.conservative-strict
  ; bounded-transmutation = λ y δ → G.zero-transmutation
  }

physics15-bridge : G.RegimeValidBridge P15.normalizationContract P15.primeExecution P15.unitRealization
physics15-bridge = record
  { classifyDelta = physics15-classify
  ; wellFormed-preserved = G.default-wellFormed-preserved P15.primeExecution P15.unitRealization
  ; strict-contraction = physics15-strict-contraction
  ; bounded-transmutation = physics15-bounded-transmutation
  }

physics19-bridge : G.RegimeValidBridge P19.normalizationContract P19.primeExecution P19.unitRealization
physics19-bridge = record
  { classifyDelta = physics19-classify
  ; wellFormed-preserved = G.default-wellFormed-preserved P19.primeExecution P19.unitRealization
  ; strict-contraction = physics19-strict-contraction
  ; bounded-transmutation = physics19-bounded-transmutation
  }

physics20-bridge : G.RegimeValidBridge P20.normalizationContract P20.primeExecution P20.unitRealization
physics20-bridge = record
  { classifyDelta = physics20-classify
  ; wellFormed-preserved = G.default-wellFormed-preserved P20.primeExecution P20.unitRealization
  ; strict-contraction = physics20-strict-contraction
  ; bounded-transmutation = physics20-bounded-transmutation
  }

physics21-bridge : G.RegimeValidBridge P21.normalizationContract P21.primeExecution P21.unitRealization
physics21-bridge = record
  { classifyDelta = physics21-classify
  ; wellFormed-preserved = G.default-wellFormed-preserved P21.primeExecution P21.unitRealization
  ; strict-contraction = physics21-strict-contraction
  ; bounded-transmutation = physics21-bounded-transmutation
  }

physics22-bridge : G.RegimeValidBridge P22.normalizationContract P22.primeExecution P22.unitRealization
physics22-bridge = record
  { classifyDelta = physics22-classify
  ; wellFormed-preserved = G.default-wellFormed-preserved P22.primeExecution P22.unitRealization
  ; strict-contraction = physics22-strict-contraction
  ; bounded-transmutation = physics22-bounded-transmutation
  }

data BridgeSlice : Set where
  S1 : BridgeSlice
  S3 : BridgeSlice
  S15 : BridgeSlice
  S19 : BridgeSlice
  S20 : BridgeSlice
  S21 : BridgeSlice
  S22 : BridgeSlice

bridgeOf : (s : BridgeSlice) →
  Set₁
bridgeOf S1 = G.RegimeValidBridge P1.normalizationContract P1.primeExecution P1.unitRealization
bridgeOf S3 = G.RegimeValidBridge P3.normalizationContract P3.primeExecution P3.unitRealization
bridgeOf S15 = G.RegimeValidBridge P15.normalizationContract P15.primeExecution P15.unitRealization
bridgeOf S19 = G.RegimeValidBridge P19.normalizationContract P19.primeExecution P19.unitRealization
bridgeOf S20 = G.RegimeValidBridge P20.normalizationContract P20.primeExecution P20.unitRealization
bridgeOf S21 = G.RegimeValidBridge P21.normalizationContract P21.primeExecution P21.unitRealization
bridgeOf S22 = G.RegimeValidBridge P22.normalizationContract P22.primeExecution P22.unitRealization

bridge-instance : (s : BridgeSlice) → bridgeOf s
bridge-instance S1 = physics1-bridge
bridge-instance S3 = physics3-bridge
bridge-instance S15 = physics15-bridge
bridge-instance S19 = physics19-bridge
bridge-instance S20 = physics20-bridge
bridge-instance S21 = physics21-bridge
bridge-instance S22 = physics22-bridge

bridge-regime-valid : (s : BridgeSlice) → bridgeOf s
bridge-regime-valid s = bridge-instance s

slice-status : (s : BridgeSlice) → Set₁
slice-status S1 = EW.ExecutionStatus (G.PrimeExecution.PrimeState P1.primeExecution)
slice-status S3 = EW.ExecutionStatus (G.PrimeExecution.PrimeState P3.primeExecution)
slice-status S15 = EW.ExecutionStatus (G.PrimeExecution.PrimeState P15.primeExecution)
slice-status S19 = EW.ExecutionStatus (G.PrimeExecution.PrimeState P19.primeExecution)
slice-status S20 = EW.ExecutionStatus (G.PrimeExecution.PrimeState P20.primeExecution)
slice-status S21 = EW.ExecutionStatus (G.PrimeExecution.PrimeState P21.primeExecution)
slice-status S22 = EW.ExecutionStatus (G.PrimeExecution.PrimeState P22.primeExecution)

statusOf : (s : BridgeSlice) → slice-status s
statusOf S1 = status1
statusOf S3 = status3
statusOf S15 = status15
statusOf S19 = status19
statusOf S20 = status20
statusOf S21 = status21
statusOf S22 = status22

delta-family : (s : BridgeSlice) → Set
delta-family S1 = P1.Delta4
delta-family S3 = P3.Delta6
delta-family S15 = P15.Delta6
delta-family S19 = P19.Delta6
delta-family S20 = P20.Delta6
delta-family S21 = P21.Delta6
delta-family S22 = P22.Delta6

classify-delta : (s : BridgeSlice) → delta-family s → G.RegimeClass
classify-delta S1 δ = physics1-classify P1.default-exp4 δ
classify-delta S3 δ = physics3-classify P3.default-exp6 δ
classify-delta S15 δ = physics15-classify P15.default-exp6 δ
classify-delta S19 δ = physics19-classify P19.default-exp6 δ
classify-delta S20 δ = physics20-classify P20.default-exp6 δ
classify-delta S21 δ = physics21-classify P21.default-exp6 δ
classify-delta S22 δ = physics22-classify P22.default-exp6 δ

------------------------------------------------------------------------
-- First numeric theorem layer:
-- target-relative residual decrease plus bounded R1/R2 transmutation.
------------------------------------------------------------------------

infixl 6 _+_
_+_ : Nat → Nat → Nat
zero + n = n
suc m + n = suc (m + n)

infix 4 _≤_
data _≤_ : Nat → Nat → Set where
  z≤n : ∀ {n} → zero ≤ n
  s≤s : ∀ {m n} → m ≤ n → suc m ≤ suc n

infix 4 _<_
_<_ : Nat → Nat → Set
m < n = suc m ≤ n

zero<positive : ∀ {n} → zero < suc n
zero<positive = s≤s z≤n

zero≤zero : zero ≤ zero
zero≤zero = z≤n

two≤two : suc (suc zero) ≤ suc (suc zero)
two≤two = s≤s (s≤s z≤n)

one≤two : suc zero ≤ suc (suc zero)
one≤two = s≤s z≤n

signed-distance : G.Signed → G.Signed → Nat
signed-distance G.negative G.negative = zero
signed-distance G.negative G.zero = suc zero
signed-distance G.negative G.positive = suc (suc zero)
signed-distance G.zero G.negative = suc zero
signed-distance G.zero G.zero = zero
signed-distance G.zero G.positive = suc zero
signed-distance G.positive G.negative = suc (suc zero)
signed-distance G.positive G.zero = suc zero
signed-distance G.positive G.positive = zero

signed-distance-self : ∀ s → signed-distance s s ≡ zero
signed-distance-self G.negative = refl
signed-distance-self G.zero = refl
signed-distance-self G.positive = refl

residual4 : P1.Exp4 → P1.Exp4 → Nat
residual4 (P1.exp4 a b c d) (P1.exp4 a' b' c' d') =
  signed-distance a a' + signed-distance b b' + signed-distance c c' + signed-distance d d'

residual4-self : ∀ y → residual4 y y ≡ zero
residual4-self (P1.exp4 a b c d)
  rewrite signed-distance-self a
        | signed-distance-self b
        | signed-distance-self c
        | signed-distance-self d = refl

residual6-3 : P3.Exp6 → P3.Exp6 → Nat
residual6-3 (P3.exp6 a b c d e f) (P3.exp6 a' b' c' d' e' f') =
  signed-distance a a' + signed-distance b b' + signed-distance c c' +
  signed-distance d d' + signed-distance e e' + signed-distance f f'

residual6-3-self : ∀ y → residual6-3 y y ≡ zero
residual6-3-self (P3.exp6 a b c d e f)
  rewrite signed-distance-self a
        | signed-distance-self b
        | signed-distance-self c
        | signed-distance-self d
        | signed-distance-self e
        | signed-distance-self f = refl

residual6-15 : P15.Exp6 → P15.Exp6 → Nat
residual6-15 (P15.exp6 a b c d e f) (P15.exp6 a' b' c' d' e' f') =
  signed-distance a a' + signed-distance b b' + signed-distance c c' +
  signed-distance d d' + signed-distance e e' + signed-distance f f'

residual6-15-self : ∀ y → residual6-15 y y ≡ zero
residual6-15-self (P15.exp6 a b c d e f)
  rewrite signed-distance-self a
        | signed-distance-self b
        | signed-distance-self c
        | signed-distance-self d
        | signed-distance-self e
        | signed-distance-self f = refl

r12-transmutation3 : P3.Exp6 → P3.Exp6 → Nat
r12-transmutation3 (P3.exp6 a b c d e f) (P3.exp6 a' b' c' d' e' f') =
  signed-distance a a' + signed-distance b b'

r12-transmutation15 : P15.Exp6 → P15.Exp6 → Nat
r12-transmutation15 (P15.exp6 a b c d e f) (P15.exp6 a' b' c' d' e' f') =
  signed-distance a a' + signed-distance b b'

class-bound : G.RegimeClass → Nat
class-bound G.conservative-contracting = zero
class-bound G.transmuting-contracting = suc (suc zero)

class-bound15 : P15.RegimeClass → Nat
class-bound15 P15.conservative-contracting = zero
class-bound15 P15.transmuting-contracting = suc (suc zero)

class-bound19 : P19.RegimeClass → Nat
class-bound19 P19.conservative-contracting = zero
class-bound19 P19.transmuting-contracting = suc (suc zero)

class-bound20 : P20.RegimeClass → Nat
class-bound20 P20.conservative-contracting = zero
class-bound20 P20.transmuting-contracting = suc (suc zero)

class-bound21 : P21.RegimeClass → Nat
class-bound21 P21.conservative-contracting = zero
class-bound21 P21.transmuting-contracting = suc (suc zero)

class-bound22 : P22.RegimeClass → Nat
class-bound22 P22.conservative-contracting = zero
class-bound22 P22.transmuting-contracting = suc (suc zero)

SliceState : BridgeSlice → Set
SliceState S1 = P1.Physics1State
SliceState S3 = P3.Physics3State
SliceState S15 = P15.Physics15State
SliceState S19 = P19.Physics19State
SliceState S20 = P20.Physics20State
SliceState S21 = P21.Physics21State
SliceState S22 = P22.Physics22State

SliceStep : (s : BridgeSlice) → SliceState s → SliceState s → Set
SliceStep S1 = P1._↦₁_
SliceStep S3 = P3._↦₃_
SliceStep S15 = P15._↦₁₅_
SliceStep S19 = P19._↦₁₉_
SliceStep S20 = P20._↦₂₀_
SliceStep S21 = P21._↦₂₁_
SliceStep S22 = P22._↦₂₂_

SliceWitness : (s : BridgeSlice) {x x' : SliceState s} → SliceStep s x x' → Set
SliceWitness S1 sx = P1.RegimeWitness sx
SliceWitness S3 sx = P3.RegimeWitness sx
SliceWitness S15 sx = P15.RegimeWitness sx
SliceWitness S19 sx = P19.RegimeWitness sx
SliceWitness S20 sx = P20.RegimeWitness sx
SliceWitness S21 sx = P21.RegimeWitness sx
SliceWitness S22 sx = P22.RegimeWitness sx

slice-regime-valid :
  (s : BridgeSlice) →
  ∀ {x x' : SliceState s} →
  (sx : SliceStep s x x') →
  SliceWitness s sx
slice-regime-valid S1 sx = P1.physics1-regime-valid sx
slice-regime-valid S3 sx = P3.physics3-regime-valid sx
slice-regime-valid S15 sx = P15.physics15-regime-valid sx
slice-regime-valid S19 sx = P19.physics19-regime-valid sx
slice-regime-valid S20 sx = P20.physics20-regime-valid sx
slice-regime-valid S21 sx = P21.physics21-regime-valid sx
slice-regime-valid S22 sx = P22.physics22-regime-valid sx

ClosedSlice : Set
ClosedSlice = Σ BridgeSlice (λ s → Σ (SliceState s) (λ x → Σ (SliceState s) (λ x' → SliceStep s x x')))

closed-slice-witness :
  (w : ClosedSlice) →
  let s = fst w in
  let xx = snd w in
  let x = fst xx in
  let xx' = snd xx in
  let x' = fst xx' in
  let sx = snd xx' in
  SliceWitness s sx
closed-slice-witness (S1 , x , x' , sx) = P1.physics1-regime-valid sx
closed-slice-witness (S3 , x , x' , sx) = P3.physics3-regime-valid sx
closed-slice-witness (S15 , x , x' , sx) = P15.physics15-regime-valid sx
closed-slice-witness (S19 , x , x' , sx) = P19.physics19-regime-valid sx
closed-slice-witness (S20 , x , x' , sx) = P20.physics20-regime-valid sx
closed-slice-witness (S21 , x , x' , sx) = P21.physics21-regime-valid sx
closed-slice-witness (S22 , x , x' , sx) = P22.physics22-regime-valid sx

ResidualToTarget : (s : BridgeSlice) → SliceState s → SliceState s → Nat
ResidualToTarget S1 x y = residual4 (P1.compile x) (P1.compile y)
ResidualToTarget S3 x y = residual6-3 (P3.compile x) (P3.compile y)
ResidualToTarget S15 x y = residual6-15 (P15.compile x) (P15.compile y)
ResidualToTarget S19 x y = residual6-15 (P19.compile x) (P19.compile y)
ResidualToTarget S20 x y = residual6-15 (P20.compile x) (P20.compile y)
ResidualToTarget S21 x y = residual6-15 (P21.compile x) (P21.compile y)
ResidualToTarget S22 x y = residual6-15 (P22.compile x) (P22.compile y)

TransmutationDelta : (s : BridgeSlice) → SliceState s → SliceState s → Nat
TransmutationDelta S1 x y = zero
TransmutationDelta S3 x y = r12-transmutation3 (P3.compile x) (P3.compile y)
TransmutationDelta S15 x y = r12-transmutation15 (P15.compile x) (P15.compile y)
TransmutationDelta S19 x y = r12-transmutation15 (P19.compile x) (P19.compile y)
TransmutationDelta S20 x y = r12-transmutation15 (P20.compile x) (P20.compile y)
TransmutationDelta S21 x y = r12-transmutation15 (P21.compile x) (P21.compile y)
TransmutationDelta S22 x y = r12-transmutation15 (P22.compile x) (P22.compile y)

TransmutationBound :
  (s : BridgeSlice) →
  ∀ {x x'} →
  SliceStep s x x' →
  Nat
TransmutationBound S1 sx = zero
TransmutationBound S3 sx = class-bound G.conservative-contracting
TransmutationBound S15 sx = class-bound15 (P15.ruleClass sx)
TransmutationBound S19 sx = class-bound19 (P19.ruleClass sx)
TransmutationBound S20 sx = class-bound20 (P20.ruleClass sx)
TransmutationBound S21 sx = class-bound21 (P21.ruleClass sx)
TransmutationBound S22 sx = class-bound22 (P22.ruleClass sx)

physics1-step-distance-decreases :
  ∀ {x x'} →
  (sx : P1._↦₁_ x x') →
  residual4 (P1.compile x') (P1.compile x') < residual4 (P1.compile x) (P1.compile x')
physics1-step-distance-decreases {x = P1.st G.negative r2 G.zero r4} {x' = x'} P1.join-left-high
  rewrite residual4-self (P1.compile x')
        | signed-distance-self r2
        | signed-distance-self r4 = zero<positive
physics1-step-distance-decreases {x = P1.st r1 G.negative G.zero r4} {x' = x'} P1.join-right-high
  rewrite residual4-self (P1.compile x')
        | signed-distance-self r1
        | signed-distance-self r4 = zero<positive
physics1-step-distance-decreases {x = P1.st G.positive r2 G.zero r4} {x' = x'} P1.join-left-mid
  rewrite residual4-self (P1.compile x')
        | signed-distance-self r2
        | signed-distance-self r4 = zero<positive
physics1-step-distance-decreases {x = P1.st r1 G.positive G.zero r4} {x' = x'} P1.join-right-mid
  rewrite residual4-self (P1.compile x')
        | signed-distance-self r1
        | signed-distance-self r4 = zero<positive
physics1-step-distance-decreases {x = P1.st r1 r2 G.negative G.positive} {x' = x'} P1.contract-high
  rewrite residual4-self (P1.compile x')
        | signed-distance-self r1
        | signed-distance-self r2 = zero<positive
physics1-step-distance-decreases {x = P1.st r1 r2 G.positive G.positive} {x' = x'} P1.contract-mid
  rewrite residual4-self (P1.compile x')
        | signed-distance-self r1
        | signed-distance-self r2 = zero<positive
physics1-step-distance-decreases {x = P1.st r1 r2 r3 G.negative} {x' = x'} P1.boundary-reset
  rewrite residual4-self (P1.compile x')
        | signed-distance-self r1
        | signed-distance-self r2
        | signed-distance-self r3 = zero<positive

physics3-step-distance-decreases :
  ∀ {x x'} →
  (sx : P3._↦₃_ x x') →
  residual6-3 (P3.compile x') (P3.compile x') < residual6-3 (P3.compile x) (P3.compile x')
physics3-step-distance-decreases {x' = x'} P3.scan-left-high
  rewrite residual6-3-self (P3.compile x') = zero<positive
physics3-step-distance-decreases {x' = x'} P3.scan-left-mid
  rewrite residual6-3-self (P3.compile x') = zero<positive
physics3-step-distance-decreases {x' = x'} P3.scan-right-high
  rewrite residual6-3-self (P3.compile x') = zero<positive
physics3-step-distance-decreases {x' = x'} P3.scan-right-mid
  rewrite residual6-3-self (P3.compile x') = zero<positive
physics3-step-distance-decreases {x' = x'} P3.join-left-high
  rewrite residual6-3-self (P3.compile x') = zero<positive
physics3-step-distance-decreases {x' = x'} P3.join-right-high
  rewrite residual6-3-self (P3.compile x') = zero<positive
physics3-step-distance-decreases {x' = x'} P3.join-left-mid
  rewrite residual6-3-self (P3.compile x') = zero<positive
physics3-step-distance-decreases {x' = x'} P3.join-right-mid
  rewrite residual6-3-self (P3.compile x') = zero<positive
physics3-step-distance-decreases {x' = x'} P3.contract-high
  rewrite residual6-3-self (P3.compile x') = zero<positive
physics3-step-distance-decreases {x' = x'} P3.contract-mid
  rewrite residual6-3-self (P3.compile x') = zero<positive
physics3-step-distance-decreases {x' = x'} P3.boundary-to-shell
  rewrite residual6-3-self (P3.compile x') = zero<positive
physics3-step-distance-decreases {x' = x'} P3.shell-to-interior
  rewrite residual6-3-self (P3.compile x') = zero<positive

physics15-step-distance-decreases :
  ∀ {x x'} →
  (sx : P15._↦₁₅_ x x') →
  residual6-15 (P15.compile x') (P15.compile x') < residual6-15 (P15.compile x) (P15.compile x')
physics15-step-distance-decreases {x' = x'} P15.physics4-scan-left-high
  rewrite residual6-15-self (P15.compile x') = zero<positive
physics15-step-distance-decreases {x' = x'} P15.physics4-scan-left-mid
  rewrite residual6-15-self (P15.compile x') = zero<positive
physics15-step-distance-decreases {x' = x'} P15.physics4-scan-right-high
  rewrite residual6-15-self (P15.compile x') = zero<positive
physics15-step-distance-decreases {x' = x'} P15.physics4-scan-right-mid
  rewrite residual6-15-self (P15.compile x') = zero<positive
physics15-step-distance-decreases {x' = x'} P15.physics2-join-left-high
  rewrite residual6-15-self (P15.compile x') = zero<positive
physics15-step-distance-decreases {x' = x'} P15.physics2-join-right-high
  rewrite residual6-15-self (P15.compile x') = zero<positive
physics15-step-distance-decreases {x' = x'} P15.physics2-join-left-mid
  rewrite residual6-15-self (P15.compile x') = zero<positive
physics15-step-distance-decreases {x' = x'} P15.physics2-join-right-mid
  rewrite residual6-15-self (P15.compile x') = zero<positive
physics15-step-distance-decreases {x' = x'} P15.physics2-contract-high
  rewrite residual6-15-self (P15.compile x') = zero<positive
physics15-step-distance-decreases {x' = x'} P15.physics2-contract-mid
  rewrite residual6-15-self (P15.compile x') = zero<positive
physics15-step-distance-decreases {x' = x'} P15.physics11-boundary-discharge
  rewrite residual6-15-self (P15.compile x') = zero<positive
physics15-step-distance-decreases {x' = x'} P15.physics5-boundary-to-shell
  rewrite residual6-15-self (P15.compile x') = zero<positive
physics15-step-distance-decreases {x' = x'} P15.physics9-shell-probe-left-high
  rewrite residual6-15-self (P15.compile x') = zero<positive
physics15-step-distance-decreases {x' = x'} P15.physics9-shell-probe-right-high
  rewrite residual6-15-self (P15.compile x') = zero<positive
physics15-step-distance-decreases {x' = x'} P15.physics9-shell-probe-left-mid
  rewrite residual6-15-self (P15.compile x') = zero<positive
physics15-step-distance-decreases {x' = x'} P15.physics9-shell-probe-right-mid
  rewrite residual6-15-self (P15.compile x') = zero<positive
physics15-step-distance-decreases {x' = x'} P15.physics9-shell-stage-release-left
  rewrite residual6-15-self (P15.compile x') = zero<positive
physics15-step-distance-decreases {x' = x'} P15.physics12-shell-stage-detour-left
  rewrite residual6-15-self (P15.compile x') = zero<positive
physics15-step-distance-decreases {x' = x'} P15.physics12-shell-stage-detour-right
  rewrite residual6-15-self (P15.compile x') = zero<positive
physics15-step-distance-decreases {x' = x'} P15.physics9-shell-stage-release-right
  rewrite residual6-15-self (P15.compile x') = zero<positive
physics15-step-distance-decreases {x' = x'} P15.physics10-shell-probe-neutral
  rewrite residual6-15-self (P15.compile x') = zero<positive
physics15-step-distance-decreases {x' = x'} P15.physics6-shell-refresh-left
  rewrite residual6-15-self (P15.compile x') = zero<positive
physics15-step-distance-decreases {x' = x'} P15.physics6-shell-refresh-right
  rewrite residual6-15-self (P15.compile x') = zero<positive
physics15-step-distance-decreases {x' = x'} P15.physics5-shell-to-interior-cleared
  rewrite residual6-15-self (P15.compile x') = zero<positive
physics15-step-distance-decreases {x' = x'} P15.physics5-shell-to-interior-latched-left
  rewrite residual6-15-self (P15.compile x') = zero<positive
physics15-step-distance-decreases {x' = x'} P15.physics5-shell-to-interior-latched-right
  rewrite residual6-15-self (P15.compile x') = zero<positive
physics15-step-distance-decreases {x' = x'} P15.physics13-contract-mid-detour-nn
  rewrite residual6-15-self (P15.compile x') = zero<positive
physics15-step-distance-decreases {x' = x'} P15.physics14-shell-high-rearm
  rewrite residual6-15-self (P15.compile x') = zero<positive
physics15-step-distance-decreases {x' = x'} P15.physics15-boundary-crossfeed-neutral
  rewrite residual6-15-self (P15.compile x') = zero<positive

physics19-step-distance-decreases :
  ∀ {x x'} →
  (sx : P19._↦₁₉_ x x') →
  residual6-15 (P19.compile x') (P19.compile x') < residual6-15 (P19.compile x) (P19.compile x')
physics19-step-distance-decreases {x' = x'} P19.physics4-scan-left-high
  rewrite residual6-15-self (P19.compile x') = zero<positive
physics19-step-distance-decreases {x' = x'} P19.physics4-scan-left-mid
  rewrite residual6-15-self (P19.compile x') = zero<positive
physics19-step-distance-decreases {x' = x'} P19.physics4-scan-right-high
  rewrite residual6-15-self (P19.compile x') = zero<positive
physics19-step-distance-decreases {x' = x'} P19.physics4-scan-right-mid
  rewrite residual6-15-self (P19.compile x') = zero<positive
physics19-step-distance-decreases {x' = x'} P19.physics2-join-left-high
  rewrite residual6-15-self (P19.compile x') = zero<positive
physics19-step-distance-decreases {x' = x'} P19.physics2-join-right-high
  rewrite residual6-15-self (P19.compile x') = zero<positive
physics19-step-distance-decreases {x' = x'} P19.physics2-join-left-mid
  rewrite residual6-15-self (P19.compile x') = zero<positive
physics19-step-distance-decreases {x' = x'} P19.physics2-join-right-mid
  rewrite residual6-15-self (P19.compile x') = zero<positive
physics19-step-distance-decreases {x' = x'} P19.physics2-contract-high
  rewrite residual6-15-self (P19.compile x') = zero<positive
physics19-step-distance-decreases {x' = x'} P19.physics2-contract-mid
  rewrite residual6-15-self (P19.compile x') = zero<positive
physics19-step-distance-decreases {x' = x'} P19.physics11-boundary-discharge
  rewrite residual6-15-self (P19.compile x') = zero<positive
physics19-step-distance-decreases {x' = x'} P19.physics5-boundary-to-shell
  rewrite residual6-15-self (P19.compile x') = zero<positive
physics19-step-distance-decreases {x' = x'} P19.physics9-shell-probe-left-high
  rewrite residual6-15-self (P19.compile x') = zero<positive
physics19-step-distance-decreases {x' = x'} P19.physics9-shell-probe-right-high
  rewrite residual6-15-self (P19.compile x') = zero<positive
physics19-step-distance-decreases {x' = x'} P19.physics9-shell-probe-left-mid
  rewrite residual6-15-self (P19.compile x') = zero<positive
physics19-step-distance-decreases {x' = x'} P19.physics9-shell-probe-right-mid
  rewrite residual6-15-self (P19.compile x') = zero<positive
physics19-step-distance-decreases {x' = x'} P19.physics9-shell-stage-release-left
  rewrite residual6-15-self (P19.compile x') = zero<positive
physics19-step-distance-decreases {x' = x'} P19.physics12-shell-stage-detour-left
  rewrite residual6-15-self (P19.compile x') = zero<positive
physics19-step-distance-decreases {x' = x'} P19.physics12-shell-stage-detour-right
  rewrite residual6-15-self (P19.compile x') = zero<positive
physics19-step-distance-decreases {x' = x'} P19.physics9-shell-stage-release-right
  rewrite residual6-15-self (P19.compile x') = zero<positive
physics19-step-distance-decreases {x' = x'} P19.physics10-shell-probe-neutral
  rewrite residual6-15-self (P19.compile x') = zero<positive
physics19-step-distance-decreases {x' = x'} P19.physics6-shell-refresh-left
  rewrite residual6-15-self (P19.compile x') = zero<positive
physics19-step-distance-decreases {x' = x'} P19.physics6-shell-refresh-right
  rewrite residual6-15-self (P19.compile x') = zero<positive
physics19-step-distance-decreases {x' = x'} P19.physics5-shell-to-interior-cleared
  rewrite residual6-15-self (P19.compile x') = zero<positive
physics19-step-distance-decreases {x' = x'} P19.physics5-shell-to-interior-latched-left
  rewrite residual6-15-self (P19.compile x') = zero<positive
physics19-step-distance-decreases {x' = x'} P19.physics5-shell-to-interior-latched-right
  rewrite residual6-15-self (P19.compile x') = zero<positive
physics19-step-distance-decreases {x' = x'} P19.physics13-contract-mid-detour-nn
  rewrite residual6-15-self (P19.compile x') = zero<positive
physics19-step-distance-decreases {x' = x'} P19.physics14-shell-high-rearm
  rewrite residual6-15-self (P19.compile x') = zero<positive
physics19-step-distance-decreases {x' = x'} P19.physics15-boundary-crossfeed-neutral
  rewrite residual6-15-self (P19.compile x') = zero<positive
physics19-step-distance-decreases {x' = x'} P19.physics16-boundary-discharge-high
  rewrite residual6-15-self (P19.compile x') = zero<positive
physics19-step-distance-decreases {x' = x'} P19.physics17-boundary-handoff-left-to-mid
  rewrite residual6-15-self (P19.compile x') = zero<positive
physics19-step-distance-decreases {x' = x'} P19.physics18-boundary-discharge-mid
  rewrite residual6-15-self (P19.compile x') = zero<positive
physics19-step-distance-decreases {x' = x'} P19.physics19-tail-handoff-n0-to-nn
  rewrite residual6-15-self (P19.compile x') = zero<positive

physics20-step-distance-decreases :
  ∀ {x x'} →
  (sx : P20._↦₂₀_ x x') →
  residual6-15 (P20.compile x') (P20.compile x') < residual6-15 (P20.compile x) (P20.compile x')
physics20-step-distance-decreases {x' = x'} P20.physics4-scan-left-high
  rewrite residual6-15-self (P20.compile x') = zero<positive
physics20-step-distance-decreases {x' = x'} P20.physics4-scan-left-mid
  rewrite residual6-15-self (P20.compile x') = zero<positive
physics20-step-distance-decreases {x' = x'} P20.physics4-scan-right-high
  rewrite residual6-15-self (P20.compile x') = zero<positive
physics20-step-distance-decreases {x' = x'} P20.physics4-scan-right-mid
  rewrite residual6-15-self (P20.compile x') = zero<positive
physics20-step-distance-decreases {x' = x'} P20.physics2-join-left-high
  rewrite residual6-15-self (P20.compile x') = zero<positive
physics20-step-distance-decreases {x' = x'} P20.physics2-join-right-high
  rewrite residual6-15-self (P20.compile x') = zero<positive
physics20-step-distance-decreases {x' = x'} P20.physics2-join-left-mid
  rewrite residual6-15-self (P20.compile x') = zero<positive
physics20-step-distance-decreases {x' = x'} P20.physics2-join-right-mid
  rewrite residual6-15-self (P20.compile x') = zero<positive
physics20-step-distance-decreases {x' = x'} P20.physics2-contract-high
  rewrite residual6-15-self (P20.compile x') = zero<positive
physics20-step-distance-decreases {x' = x'} P20.physics2-contract-mid
  rewrite residual6-15-self (P20.compile x') = zero<positive
physics20-step-distance-decreases {x' = x'} P20.physics11-boundary-discharge
  rewrite residual6-15-self (P20.compile x') = zero<positive
physics20-step-distance-decreases {x' = x'} P20.physics5-boundary-to-shell
  rewrite residual6-15-self (P20.compile x') = zero<positive
physics20-step-distance-decreases {x' = x'} P20.physics9-shell-probe-left-high
  rewrite residual6-15-self (P20.compile x') = zero<positive
physics20-step-distance-decreases {x' = x'} P20.physics9-shell-probe-right-high
  rewrite residual6-15-self (P20.compile x') = zero<positive
physics20-step-distance-decreases {x' = x'} P20.physics9-shell-probe-left-mid
  rewrite residual6-15-self (P20.compile x') = zero<positive
physics20-step-distance-decreases {x' = x'} P20.physics9-shell-probe-right-mid
  rewrite residual6-15-self (P20.compile x') = zero<positive
physics20-step-distance-decreases {x' = x'} P20.physics9-shell-stage-release-left
  rewrite residual6-15-self (P20.compile x') = zero<positive
physics20-step-distance-decreases {x' = x'} P20.physics12-shell-stage-detour-left
  rewrite residual6-15-self (P20.compile x') = zero<positive
physics20-step-distance-decreases {x' = x'} P20.physics12-shell-stage-detour-right
  rewrite residual6-15-self (P20.compile x') = zero<positive
physics20-step-distance-decreases {x' = x'} P20.physics9-shell-stage-release-right
  rewrite residual6-15-self (P20.compile x') = zero<positive
physics20-step-distance-decreases {x' = x'} P20.physics10-shell-probe-neutral
  rewrite residual6-15-self (P20.compile x') = zero<positive
physics20-step-distance-decreases {x' = x'} P20.physics6-shell-refresh-left
  rewrite residual6-15-self (P20.compile x') = zero<positive
physics20-step-distance-decreases {x' = x'} P20.physics6-shell-refresh-right
  rewrite residual6-15-self (P20.compile x') = zero<positive
physics20-step-distance-decreases {x' = x'} P20.physics5-shell-to-interior-cleared
  rewrite residual6-15-self (P20.compile x') = zero<positive
physics20-step-distance-decreases {x' = x'} P20.physics5-shell-to-interior-latched-left
  rewrite residual6-15-self (P20.compile x') = zero<positive
physics20-step-distance-decreases {x' = x'} P20.physics5-shell-to-interior-latched-right
  rewrite residual6-15-self (P20.compile x') = zero<positive
physics20-step-distance-decreases {x' = x'} P20.physics13-contract-mid-detour-nn
  rewrite residual6-15-self (P20.compile x') = zero<positive
physics20-step-distance-decreases {x' = x'} P20.physics14-shell-high-rearm
  rewrite residual6-15-self (P20.compile x') = zero<positive
physics20-step-distance-decreases {x' = x'} P20.physics15-boundary-crossfeed-neutral
  rewrite residual6-15-self (P20.compile x') = zero<positive
physics20-step-distance-decreases {x' = x'} P20.physics16-boundary-discharge-high
  rewrite residual6-15-self (P20.compile x') = zero<positive
physics20-step-distance-decreases {x' = x'} P20.physics17-boundary-handoff-left-to-mid
  rewrite residual6-15-self (P20.compile x') = zero<positive
physics20-step-distance-decreases {x' = x'} P20.physics18-boundary-discharge-mid
  rewrite residual6-15-self (P20.compile x') = zero<positive
physics20-step-distance-decreases {x' = x'} P20.physics20-tail-handoff-n0-to-nn
  rewrite residual6-15-self (P20.compile x') = zero<positive
physics20-step-distance-decreases {x' = x'} P20.physics20-boundary-positive-discharge
  rewrite residual6-15-self (P20.compile x') = zero<positive

physics21-step-distance-decreases :
  ∀ {x x'} →
  (sx : P21._↦₂₁_ x x') →
  residual6-15 (P21.compile x') (P21.compile x') < residual6-15 (P21.compile x) (P21.compile x')
physics21-step-distance-decreases {x' = x'} P21.physics4-scan-left-high
  rewrite residual6-15-self (P21.compile x') = zero<positive
physics21-step-distance-decreases {x' = x'} P21.physics4-scan-left-mid
  rewrite residual6-15-self (P21.compile x') = zero<positive
physics21-step-distance-decreases {x' = x'} P21.physics4-scan-right-high
  rewrite residual6-15-self (P21.compile x') = zero<positive
physics21-step-distance-decreases {x' = x'} P21.physics4-scan-right-mid
  rewrite residual6-15-self (P21.compile x') = zero<positive
physics21-step-distance-decreases {x' = x'} P21.physics2-join-left-high
  rewrite residual6-15-self (P21.compile x') = zero<positive
physics21-step-distance-decreases {x' = x'} P21.physics2-join-right-high
  rewrite residual6-15-self (P21.compile x') = zero<positive
physics21-step-distance-decreases {x' = x'} P21.physics2-join-left-mid
  rewrite residual6-15-self (P21.compile x') = zero<positive
physics21-step-distance-decreases {x' = x'} P21.physics2-join-right-mid
  rewrite residual6-15-self (P21.compile x') = zero<positive
physics21-step-distance-decreases {x' = x'} P21.physics2-contract-high
  rewrite residual6-15-self (P21.compile x') = zero<positive
physics21-step-distance-decreases {x' = x'} P21.physics2-contract-mid
  rewrite residual6-15-self (P21.compile x') = zero<positive
physics21-step-distance-decreases {x' = x'} P21.physics11-boundary-discharge
  rewrite residual6-15-self (P21.compile x') = zero<positive
physics21-step-distance-decreases {x' = x'} P21.physics5-boundary-to-shell
  rewrite residual6-15-self (P21.compile x') = zero<positive
physics21-step-distance-decreases {x' = x'} P21.physics9-shell-probe-left-high
  rewrite residual6-15-self (P21.compile x') = zero<positive
physics21-step-distance-decreases {x' = x'} P21.physics9-shell-probe-right-high
  rewrite residual6-15-self (P21.compile x') = zero<positive
physics21-step-distance-decreases {x' = x'} P21.physics9-shell-probe-left-mid
  rewrite residual6-15-self (P21.compile x') = zero<positive
physics21-step-distance-decreases {x' = x'} P21.physics9-shell-probe-right-mid
  rewrite residual6-15-self (P21.compile x') = zero<positive
physics21-step-distance-decreases {x' = x'} P21.physics9-shell-stage-release-left
  rewrite residual6-15-self (P21.compile x') = zero<positive
physics21-step-distance-decreases {x' = x'} P21.physics12-shell-stage-detour-left
  rewrite residual6-15-self (P21.compile x') = zero<positive
physics21-step-distance-decreases {x' = x'} P21.physics12-shell-stage-detour-right
  rewrite residual6-15-self (P21.compile x') = zero<positive
physics21-step-distance-decreases {x' = x'} P21.physics9-shell-stage-release-right
  rewrite residual6-15-self (P21.compile x') = zero<positive
physics21-step-distance-decreases {x' = x'} P21.physics10-shell-probe-neutral
  rewrite residual6-15-self (P21.compile x') = zero<positive
physics21-step-distance-decreases {x' = x'} P21.physics6-shell-refresh-left
  rewrite residual6-15-self (P21.compile x') = zero<positive
physics21-step-distance-decreases {x' = x'} P21.physics6-shell-refresh-right
  rewrite residual6-15-self (P21.compile x') = zero<positive
physics21-step-distance-decreases {x' = x'} P21.physics5-shell-to-interior-cleared
  rewrite residual6-15-self (P21.compile x') = zero<positive
physics21-step-distance-decreases {x' = x'} P21.physics5-shell-to-interior-latched-left
  rewrite residual6-15-self (P21.compile x') = zero<positive
physics21-step-distance-decreases {x' = x'} P21.physics5-shell-to-interior-latched-right
  rewrite residual6-15-self (P21.compile x') = zero<positive
physics21-step-distance-decreases {x' = x'} P21.physics13-contract-mid-detour-nn
  rewrite residual6-15-self (P21.compile x') = zero<positive
physics21-step-distance-decreases {x' = x'} P21.physics14-shell-high-rearm
  rewrite residual6-15-self (P21.compile x') = zero<positive
physics21-step-distance-decreases {x' = x'} P21.physics15-boundary-crossfeed-neutral
  rewrite residual6-15-self (P21.compile x') = zero<positive
physics21-step-distance-decreases {x' = x'} P21.physics16-boundary-discharge-high
  rewrite residual6-15-self (P21.compile x') = zero<positive
physics21-step-distance-decreases {x' = x'} P21.physics17-boundary-handoff-left-to-mid
  rewrite residual6-15-self (P21.compile x') = zero<positive
physics21-step-distance-decreases {x' = x'} P21.physics18-boundary-discharge-mid
  rewrite residual6-15-self (P21.compile x') = zero<positive
physics21-step-distance-decreases {x' = x'} P21.physics19-tail-handoff-n0-to-nn
  rewrite residual6-15-self (P21.compile x') = zero<positive
physics21-step-distance-decreases {x' = x'} P21.physics20-boundary-positive-discharge
  rewrite residual6-15-self (P21.compile x') = zero<positive
physics21-step-distance-decreases {x' = x'} P21.physics21-boundary-direct-reentry-mid
  rewrite residual6-15-self (P21.compile x') = zero<positive

physics22-step-distance-decreases :
  ∀ {x x'} →
  (sx : P22._↦₂₂_ x x') →
  residual6-15 (P22.compile x') (P22.compile x') < residual6-15 (P22.compile x) (P22.compile x')
physics22-step-distance-decreases {x' = x'} P22.physics4-scan-left-high
  rewrite residual6-15-self (P22.compile x') = zero<positive
physics22-step-distance-decreases {x' = x'} P22.physics4-scan-left-mid
  rewrite residual6-15-self (P22.compile x') = zero<positive
physics22-step-distance-decreases {x' = x'} P22.physics4-scan-right-high
  rewrite residual6-15-self (P22.compile x') = zero<positive
physics22-step-distance-decreases {x' = x'} P22.physics4-scan-right-mid
  rewrite residual6-15-self (P22.compile x') = zero<positive
physics22-step-distance-decreases {x' = x'} P22.physics2-join-left-high
  rewrite residual6-15-self (P22.compile x') = zero<positive
physics22-step-distance-decreases {x' = x'} P22.physics2-join-right-high
  rewrite residual6-15-self (P22.compile x') = zero<positive
physics22-step-distance-decreases {x' = x'} P22.physics2-join-left-mid
  rewrite residual6-15-self (P22.compile x') = zero<positive
physics22-step-distance-decreases {x' = x'} P22.physics2-join-right-mid
  rewrite residual6-15-self (P22.compile x') = zero<positive
physics22-step-distance-decreases {x' = x'} P22.physics2-contract-high
  rewrite residual6-15-self (P22.compile x') = zero<positive
physics22-step-distance-decreases {x' = x'} P22.physics2-contract-mid
  rewrite residual6-15-self (P22.compile x') = zero<positive
physics22-step-distance-decreases {x' = x'} P22.physics11-boundary-discharge
  rewrite residual6-15-self (P22.compile x') = zero<positive
physics22-step-distance-decreases {x' = x'} P22.physics5-boundary-to-shell
  rewrite residual6-15-self (P22.compile x') = zero<positive
physics22-step-distance-decreases {x' = x'} P22.physics9-shell-probe-left-high
  rewrite residual6-15-self (P22.compile x') = zero<positive
physics22-step-distance-decreases {x' = x'} P22.physics9-shell-probe-right-high
  rewrite residual6-15-self (P22.compile x') = zero<positive
physics22-step-distance-decreases {x' = x'} P22.physics9-shell-probe-left-mid
  rewrite residual6-15-self (P22.compile x') = zero<positive
physics22-step-distance-decreases {x' = x'} P22.physics9-shell-probe-right-mid
  rewrite residual6-15-self (P22.compile x') = zero<positive
physics22-step-distance-decreases {x' = x'} P22.physics9-shell-stage-release-left
  rewrite residual6-15-self (P22.compile x') = zero<positive
physics22-step-distance-decreases {x' = x'} P22.physics12-shell-stage-detour-left
  rewrite residual6-15-self (P22.compile x') = zero<positive
physics22-step-distance-decreases {x' = x'} P22.physics12-shell-stage-detour-right
  rewrite residual6-15-self (P22.compile x') = zero<positive
physics22-step-distance-decreases {x' = x'} P22.physics9-shell-stage-release-right
  rewrite residual6-15-self (P22.compile x') = zero<positive
physics22-step-distance-decreases {x' = x'} P22.physics10-shell-probe-neutral
  rewrite residual6-15-self (P22.compile x') = zero<positive
physics22-step-distance-decreases {x' = x'} P22.physics6-shell-refresh-left
  rewrite residual6-15-self (P22.compile x') = zero<positive
physics22-step-distance-decreases {x' = x'} P22.physics6-shell-refresh-right
  rewrite residual6-15-self (P22.compile x') = zero<positive
physics22-step-distance-decreases {x' = x'} P22.physics5-shell-to-interior-cleared
  rewrite residual6-15-self (P22.compile x') = zero<positive
physics22-step-distance-decreases {x' = x'} P22.physics5-shell-to-interior-latched-left
  rewrite residual6-15-self (P22.compile x') = zero<positive
physics22-step-distance-decreases {x' = x'} P22.physics5-shell-to-interior-latched-right
  rewrite residual6-15-self (P22.compile x') = zero<positive
physics22-step-distance-decreases {x' = x'} P22.physics13-contract-mid-detour-nn
  rewrite residual6-15-self (P22.compile x') = zero<positive
physics22-step-distance-decreases {x' = x'} P22.physics14-shell-high-rearm
  rewrite residual6-15-self (P22.compile x') = zero<positive
physics22-step-distance-decreases {x' = x'} P22.physics15-boundary-crossfeed-neutral
  rewrite residual6-15-self (P22.compile x') = zero<positive
physics22-step-distance-decreases {x' = x'} P22.physics16-boundary-discharge-high
  rewrite residual6-15-self (P22.compile x') = zero<positive
physics22-step-distance-decreases {x' = x'} P22.physics17-boundary-handoff-left-to-mid
  rewrite residual6-15-self (P22.compile x') = zero<positive
physics22-step-distance-decreases {x' = x'} P22.physics18-boundary-discharge-mid
  rewrite residual6-15-self (P22.compile x') = zero<positive
physics22-step-distance-decreases {x' = x'} P22.physics19-tail-handoff-n0-to-nn
  rewrite residual6-15-self (P22.compile x') = zero<positive
physics22-step-distance-decreases {x' = x'} P22.physics20-boundary-positive-discharge
  rewrite residual6-15-self (P22.compile x') = zero<positive
physics22-step-distance-decreases {x' = x'} P22.physics21-boundary-direct-reentry-mid
  rewrite residual6-15-self (P22.compile x') = zero<positive
physics22-step-distance-decreases {x' = x'} P22.physics22-boundary-direct-reentry-high
  rewrite residual6-15-self (P22.compile x') = zero<positive

physics3-transmutation-bounded :
  ∀ {x x'} →
  (sx : P3._↦₃_ x x') →
  r12-transmutation3 (P3.compile x) (P3.compile x') ≤ class-bound G.conservative-contracting
physics3-transmutation-bounded P3.scan-left-high = zero≤zero
physics3-transmutation-bounded P3.scan-left-mid = zero≤zero
physics3-transmutation-bounded P3.scan-right-high = zero≤zero
physics3-transmutation-bounded P3.scan-right-mid = zero≤zero
physics3-transmutation-bounded P3.join-left-high = zero≤zero
physics3-transmutation-bounded P3.join-right-high = zero≤zero
physics3-transmutation-bounded P3.join-left-mid = zero≤zero
physics3-transmutation-bounded P3.join-right-mid = zero≤zero
physics3-transmutation-bounded P3.contract-high = zero≤zero
physics3-transmutation-bounded P3.contract-mid = zero≤zero
physics3-transmutation-bounded P3.boundary-to-shell = zero≤zero
physics3-transmutation-bounded P3.shell-to-interior = zero≤zero

physics15-transmutation-bounded :
  ∀ {x x'} →
  (sx : P15._↦₁₅_ x x') →
  r12-transmutation15 (P15.compile x) (P15.compile x') ≤ class-bound15 (P15.ruleClass sx)
physics15-transmutation-bounded P15.physics4-scan-left-high = zero≤zero
physics15-transmutation-bounded P15.physics4-scan-left-mid = zero≤zero
physics15-transmutation-bounded P15.physics4-scan-right-high = zero≤zero
physics15-transmutation-bounded P15.physics4-scan-right-mid = zero≤zero
physics15-transmutation-bounded P15.physics2-join-left-high = zero≤zero
physics15-transmutation-bounded P15.physics2-join-right-high = zero≤zero
physics15-transmutation-bounded P15.physics2-join-left-mid = zero≤zero
physics15-transmutation-bounded P15.physics2-join-right-mid = zero≤zero
physics15-transmutation-bounded P15.physics2-contract-high = zero≤zero
physics15-transmutation-bounded P15.physics2-contract-mid = zero≤zero
physics15-transmutation-bounded P15.physics11-boundary-discharge = zero≤zero
physics15-transmutation-bounded P15.physics5-boundary-to-shell = zero≤zero
physics15-transmutation-bounded P15.physics9-shell-probe-left-high = zero≤zero
physics15-transmutation-bounded P15.physics9-shell-probe-right-high = zero≤zero
physics15-transmutation-bounded P15.physics9-shell-probe-left-mid = zero≤zero
physics15-transmutation-bounded P15.physics9-shell-probe-right-mid = zero≤zero
physics15-transmutation-bounded P15.physics9-shell-stage-release-left = zero≤zero
physics15-transmutation-bounded P15.physics12-shell-stage-detour-left = zero≤zero
physics15-transmutation-bounded P15.physics12-shell-stage-detour-right = zero≤zero
physics15-transmutation-bounded P15.physics9-shell-stage-release-right = zero≤zero
physics15-transmutation-bounded P15.physics10-shell-probe-neutral = zero≤zero
physics15-transmutation-bounded P15.physics6-shell-refresh-left = zero≤zero
physics15-transmutation-bounded P15.physics6-shell-refresh-right = zero≤zero
physics15-transmutation-bounded P15.physics5-shell-to-interior-cleared = zero≤zero
physics15-transmutation-bounded P15.physics5-shell-to-interior-latched-left = zero≤zero
physics15-transmutation-bounded P15.physics5-shell-to-interior-latched-right = zero≤zero
physics15-transmutation-bounded P15.physics13-contract-mid-detour-nn = zero≤zero
physics15-transmutation-bounded P15.physics14-shell-high-rearm = zero≤zero
physics15-transmutation-bounded P15.physics15-boundary-crossfeed-neutral = two≤two

physics20-transmutation-bounded :
  ∀ {x x'} →
  (sx : P20._↦₂₀_ x x') →
  r12-transmutation15 (P20.compile x) (P20.compile x') ≤ class-bound20 (P20.ruleClass sx)
physics20-transmutation-bounded P20.physics4-scan-left-high = zero≤zero
physics20-transmutation-bounded P20.physics4-scan-left-mid = zero≤zero
physics20-transmutation-bounded P20.physics4-scan-right-high = zero≤zero
physics20-transmutation-bounded P20.physics4-scan-right-mid = zero≤zero
physics20-transmutation-bounded P20.physics2-join-left-high = zero≤zero
physics20-transmutation-bounded P20.physics2-join-right-high = zero≤zero
physics20-transmutation-bounded P20.physics2-join-left-mid = zero≤zero
physics20-transmutation-bounded P20.physics2-join-right-mid = zero≤zero
physics20-transmutation-bounded P20.physics2-contract-high = zero≤zero
physics20-transmutation-bounded P20.physics2-contract-mid = zero≤zero
physics20-transmutation-bounded P20.physics11-boundary-discharge = zero≤zero
physics20-transmutation-bounded P20.physics5-boundary-to-shell = zero≤zero
physics20-transmutation-bounded P20.physics9-shell-probe-left-high = zero≤zero
physics20-transmutation-bounded P20.physics9-shell-probe-right-high = zero≤zero
physics20-transmutation-bounded P20.physics9-shell-probe-left-mid = zero≤zero
physics20-transmutation-bounded P20.physics9-shell-probe-right-mid = zero≤zero
physics20-transmutation-bounded P20.physics9-shell-stage-release-left = zero≤zero
physics20-transmutation-bounded P20.physics12-shell-stage-detour-left = zero≤zero
physics20-transmutation-bounded P20.physics12-shell-stage-detour-right = zero≤zero
physics20-transmutation-bounded P20.physics9-shell-stage-release-right = zero≤zero
physics20-transmutation-bounded P20.physics10-shell-probe-neutral = zero≤zero
physics20-transmutation-bounded P20.physics6-shell-refresh-left = zero≤zero
physics20-transmutation-bounded P20.physics6-shell-refresh-right = zero≤zero
physics20-transmutation-bounded P20.physics5-shell-to-interior-cleared = zero≤zero
physics20-transmutation-bounded P20.physics5-shell-to-interior-latched-left = zero≤zero
physics20-transmutation-bounded P20.physics5-shell-to-interior-latched-right = zero≤zero
physics20-transmutation-bounded P20.physics13-contract-mid-detour-nn = zero≤zero
physics20-transmutation-bounded P20.physics14-shell-high-rearm = zero≤zero
physics20-transmutation-bounded P20.physics15-boundary-crossfeed-neutral = two≤two
physics20-transmutation-bounded P20.physics16-boundary-discharge-high = zero≤zero
physics20-transmutation-bounded P20.physics17-boundary-handoff-left-to-mid = one≤two
physics20-transmutation-bounded P20.physics18-boundary-discharge-mid = zero≤zero
physics20-transmutation-bounded P20.physics20-tail-handoff-n0-to-nn = one≤two
physics20-transmutation-bounded P20.physics20-boundary-positive-discharge = zero≤zero

physics21-transmutation-bounded :
  ∀ {x x'} →
  (sx : P21._↦₂₁_ x x') →
  r12-transmutation15 (P21.compile x) (P21.compile x') ≤ class-bound21 (P21.ruleClass sx)
physics21-transmutation-bounded P21.physics4-scan-left-high = zero≤zero
physics21-transmutation-bounded P21.physics4-scan-left-mid = zero≤zero
physics21-transmutation-bounded P21.physics4-scan-right-high = zero≤zero
physics21-transmutation-bounded P21.physics4-scan-right-mid = zero≤zero
physics21-transmutation-bounded P21.physics2-join-left-high = zero≤zero
physics21-transmutation-bounded P21.physics2-join-right-high = zero≤zero
physics21-transmutation-bounded P21.physics2-join-left-mid = zero≤zero
physics21-transmutation-bounded P21.physics2-join-right-mid = zero≤zero
physics21-transmutation-bounded P21.physics2-contract-high = zero≤zero
physics21-transmutation-bounded P21.physics2-contract-mid = zero≤zero
physics21-transmutation-bounded P21.physics11-boundary-discharge = zero≤zero
physics21-transmutation-bounded P21.physics5-boundary-to-shell = zero≤zero
physics21-transmutation-bounded P21.physics9-shell-probe-left-high = zero≤zero
physics21-transmutation-bounded P21.physics9-shell-probe-right-high = zero≤zero
physics21-transmutation-bounded P21.physics9-shell-probe-left-mid = zero≤zero
physics21-transmutation-bounded P21.physics9-shell-probe-right-mid = zero≤zero
physics21-transmutation-bounded P21.physics9-shell-stage-release-left = zero≤zero
physics21-transmutation-bounded P21.physics12-shell-stage-detour-left = zero≤zero
physics21-transmutation-bounded P21.physics12-shell-stage-detour-right = zero≤zero
physics21-transmutation-bounded P21.physics9-shell-stage-release-right = zero≤zero
physics21-transmutation-bounded P21.physics10-shell-probe-neutral = zero≤zero
physics21-transmutation-bounded P21.physics6-shell-refresh-left = zero≤zero
physics21-transmutation-bounded P21.physics6-shell-refresh-right = zero≤zero
physics21-transmutation-bounded P21.physics5-shell-to-interior-cleared = zero≤zero
physics21-transmutation-bounded P21.physics5-shell-to-interior-latched-left = zero≤zero
physics21-transmutation-bounded P21.physics5-shell-to-interior-latched-right = zero≤zero
physics21-transmutation-bounded P21.physics13-contract-mid-detour-nn = zero≤zero
physics21-transmutation-bounded P21.physics14-shell-high-rearm = zero≤zero
physics21-transmutation-bounded P21.physics15-boundary-crossfeed-neutral = two≤two
physics21-transmutation-bounded P21.physics16-boundary-discharge-high = zero≤zero
physics21-transmutation-bounded P21.physics17-boundary-handoff-left-to-mid = one≤two
physics21-transmutation-bounded P21.physics18-boundary-discharge-mid = zero≤zero
physics21-transmutation-bounded P21.physics19-tail-handoff-n0-to-nn = one≤two
physics21-transmutation-bounded P21.physics20-boundary-positive-discharge = zero≤zero
physics21-transmutation-bounded P21.physics21-boundary-direct-reentry-mid = zero≤zero

physics22-transmutation-bounded :
  ∀ {x x'} →
  (sx : P22._↦₂₂_ x x') →
  r12-transmutation15 (P22.compile x) (P22.compile x') ≤ class-bound22 (P22.ruleClass sx)
physics22-transmutation-bounded P22.physics4-scan-left-high = zero≤zero
physics22-transmutation-bounded P22.physics4-scan-left-mid = zero≤zero
physics22-transmutation-bounded P22.physics4-scan-right-high = zero≤zero
physics22-transmutation-bounded P22.physics4-scan-right-mid = zero≤zero
physics22-transmutation-bounded P22.physics2-join-left-high = zero≤zero
physics22-transmutation-bounded P22.physics2-join-right-high = zero≤zero
physics22-transmutation-bounded P22.physics2-join-left-mid = zero≤zero
physics22-transmutation-bounded P22.physics2-join-right-mid = zero≤zero
physics22-transmutation-bounded P22.physics2-contract-high = zero≤zero
physics22-transmutation-bounded P22.physics2-contract-mid = zero≤zero
physics22-transmutation-bounded P22.physics11-boundary-discharge = zero≤zero
physics22-transmutation-bounded P22.physics5-boundary-to-shell = zero≤zero
physics22-transmutation-bounded P22.physics9-shell-probe-left-high = zero≤zero
physics22-transmutation-bounded P22.physics9-shell-probe-right-high = zero≤zero
physics22-transmutation-bounded P22.physics9-shell-probe-left-mid = zero≤zero
physics22-transmutation-bounded P22.physics9-shell-probe-right-mid = zero≤zero
physics22-transmutation-bounded P22.physics9-shell-stage-release-left = zero≤zero
physics22-transmutation-bounded P22.physics12-shell-stage-detour-left = zero≤zero
physics22-transmutation-bounded P22.physics12-shell-stage-detour-right = zero≤zero
physics22-transmutation-bounded P22.physics9-shell-stage-release-right = zero≤zero
physics22-transmutation-bounded P22.physics10-shell-probe-neutral = zero≤zero
physics22-transmutation-bounded P22.physics6-shell-refresh-left = zero≤zero
physics22-transmutation-bounded P22.physics6-shell-refresh-right = zero≤zero
physics22-transmutation-bounded P22.physics5-shell-to-interior-cleared = zero≤zero
physics22-transmutation-bounded P22.physics5-shell-to-interior-latched-left = zero≤zero
physics22-transmutation-bounded P22.physics5-shell-to-interior-latched-right = zero≤zero
physics22-transmutation-bounded P22.physics13-contract-mid-detour-nn = zero≤zero
physics22-transmutation-bounded P22.physics14-shell-high-rearm = zero≤zero
physics22-transmutation-bounded P22.physics15-boundary-crossfeed-neutral = two≤two
physics22-transmutation-bounded P22.physics16-boundary-discharge-high = zero≤zero
physics22-transmutation-bounded P22.physics17-boundary-handoff-left-to-mid = one≤two
physics22-transmutation-bounded P22.physics18-boundary-discharge-mid = zero≤zero
physics22-transmutation-bounded P22.physics19-tail-handoff-n0-to-nn = one≤two
physics22-transmutation-bounded P22.physics20-boundary-positive-discharge = zero≤zero
physics22-transmutation-bounded P22.physics21-boundary-direct-reentry-mid = zero≤zero
physics22-transmutation-bounded P22.physics22-boundary-direct-reentry-high = zero≤zero

physics19-transmutation-bounded :
  ∀ {x x'} →
  (sx : P19._↦₁₉_ x x') →
  r12-transmutation15 (P19.compile x) (P19.compile x') ≤ class-bound19 (P19.ruleClass sx)
physics19-transmutation-bounded P19.physics4-scan-left-high = zero≤zero
physics19-transmutation-bounded P19.physics4-scan-left-mid = zero≤zero
physics19-transmutation-bounded P19.physics4-scan-right-high = zero≤zero
physics19-transmutation-bounded P19.physics4-scan-right-mid = zero≤zero
physics19-transmutation-bounded P19.physics2-join-left-high = zero≤zero
physics19-transmutation-bounded P19.physics2-join-right-high = zero≤zero
physics19-transmutation-bounded P19.physics2-join-left-mid = zero≤zero
physics19-transmutation-bounded P19.physics2-join-right-mid = zero≤zero
physics19-transmutation-bounded P19.physics2-contract-high = zero≤zero
physics19-transmutation-bounded P19.physics2-contract-mid = zero≤zero
physics19-transmutation-bounded P19.physics11-boundary-discharge = zero≤zero
physics19-transmutation-bounded P19.physics5-boundary-to-shell = zero≤zero
physics19-transmutation-bounded P19.physics9-shell-probe-left-high = zero≤zero
physics19-transmutation-bounded P19.physics9-shell-probe-right-high = zero≤zero
physics19-transmutation-bounded P19.physics9-shell-probe-left-mid = zero≤zero
physics19-transmutation-bounded P19.physics9-shell-probe-right-mid = zero≤zero
physics19-transmutation-bounded P19.physics9-shell-stage-release-left = zero≤zero
physics19-transmutation-bounded P19.physics12-shell-stage-detour-left = zero≤zero
physics19-transmutation-bounded P19.physics12-shell-stage-detour-right = zero≤zero
physics19-transmutation-bounded P19.physics9-shell-stage-release-right = zero≤zero
physics19-transmutation-bounded P19.physics10-shell-probe-neutral = zero≤zero
physics19-transmutation-bounded P19.physics6-shell-refresh-left = zero≤zero
physics19-transmutation-bounded P19.physics6-shell-refresh-right = zero≤zero
physics19-transmutation-bounded P19.physics5-shell-to-interior-cleared = zero≤zero
physics19-transmutation-bounded P19.physics5-shell-to-interior-latched-left = zero≤zero
physics19-transmutation-bounded P19.physics5-shell-to-interior-latched-right = zero≤zero
physics19-transmutation-bounded P19.physics13-contract-mid-detour-nn = zero≤zero
physics19-transmutation-bounded P19.physics14-shell-high-rearm = zero≤zero
physics19-transmutation-bounded P19.physics15-boundary-crossfeed-neutral = two≤two
physics19-transmutation-bounded P19.physics16-boundary-discharge-high = zero≤zero
physics19-transmutation-bounded P19.physics17-boundary-handoff-left-to-mid = one≤two
physics19-transmutation-bounded P19.physics18-boundary-discharge-mid = zero≤zero
physics19-transmutation-bounded P19.physics19-tail-handoff-n0-to-nn = one≤two

slice-step-distance-decreases :
  (s : BridgeSlice) →
  ∀ {x x'} →
  (sx : SliceStep s x x') →
  ResidualToTarget s x' x' < ResidualToTarget s x x'
slice-step-distance-decreases S1 sx = physics1-step-distance-decreases sx
slice-step-distance-decreases S3 sx = physics3-step-distance-decreases sx
slice-step-distance-decreases S15 sx = physics15-step-distance-decreases sx
slice-step-distance-decreases S19 sx = physics19-step-distance-decreases sx
slice-step-distance-decreases S20 sx = physics20-step-distance-decreases sx
slice-step-distance-decreases S21 sx = physics21-step-distance-decreases sx
slice-step-distance-decreases S22 sx = physics22-step-distance-decreases sx

slice-transmutation-bounded :
  (s : BridgeSlice) →
  ∀ {x x'} →
  (sx : SliceStep s x x') →
  TransmutationDelta s x x' ≤ TransmutationBound s sx
slice-transmutation-bounded S1 sx = zero≤zero
slice-transmutation-bounded S3 sx = physics3-transmutation-bounded sx
slice-transmutation-bounded S15 sx = physics15-transmutation-bounded sx
slice-transmutation-bounded S19 sx = physics19-transmutation-bounded sx
slice-transmutation-bounded S20 sx = physics20-transmutation-bounded sx
slice-transmutation-bounded S21 sx = physics21-transmutation-bounded sx
slice-transmutation-bounded S22 sx = physics22-transmutation-bounded sx
