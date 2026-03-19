module formalism.GenericMacroBridge where

open import Agda.Builtin.Equality using (_≡_; refl)
open import Agda.Builtin.List using (List; []; _∷_)
open import Agda.Builtin.Nat using (Nat; zero; suc)
open import Agda.Builtin.Sigma using (Σ; _,_)
open import Agda.Builtin.Unit using (⊤; tt)

data Signed : Set where
  negative : Signed
  zero     : Signed
  positive : Signed

data DeltaVal : Set where
  dm2 : DeltaVal
  dm1 : DeltaVal
  d0  : DeltaVal
  dp1 : DeltaVal
  dp2 : DeltaVal

data StepSign : Set where
  up : StepSign
  down : StepSign

data RegimeClass : Set where
  conservative-contracting : RegimeClass
  transmuting-contracting : RegimeClass

data StrictContractionWitness : RegimeClass → Set where
  conservative-strict : StrictContractionWitness conservative-contracting
  transmuting-strict : StrictContractionWitness transmuting-contracting

data BoundedTransmutationWitness : RegimeClass → Set where
  zero-transmutation : BoundedTransmutationWitness conservative-contracting
  bounded-transmutation-witness : BoundedTransmutationWitness transmuting-contracting

classTransmutationBound : RegimeClass → Nat
classTransmutationBound conservative-contracting = zero
classTransmutationBound transmuting-contracting = suc (suc zero)

classStrictContractionStep : RegimeClass → Nat
classStrictContractionStep conservative-contracting = suc zero
classStrictContractionStep transmuting-contracting = suc zero

strictContractionStepOf :
  ∀ {c : RegimeClass} →
  StrictContractionWitness c → Nat
strictContractionStepOf {c} w = classStrictContractionStep c

transmutationBoundOf :
  ∀ {c : RegimeClass} →
  BoundedTransmutationWitness c → Nat
transmutationBoundOf {c} w = classTransmutationBound c

addSigned : Signed → DeltaVal → Signed
addSigned s        d0  = s
addSigned negative dm2 = negative
addSigned negative dm1 = negative
addSigned negative dp1 = zero
addSigned negative dp2 = positive
addSigned zero     dm2 = negative
addSigned zero     dm1 = negative
addSigned zero     dp1 = positive
addSigned zero     dp2 = positive
addSigned positive dm2 = negative
addSigned positive dm1 = zero
addSigned positive dp1 = positive
addSigned positive dp2 = positive

record UnitDelta (Coord : Set) : Set where
  constructor unit
  field
    coord : Coord
    sign  : StepSign

open UnitDelta public

unitDeltaValue : StepSign → DeltaVal
unitDeltaValue up = dp1
unitDeltaValue down = dm1

append : ∀ {A : Set} → List A → List A → List A
append [] ys = ys
append (x ∷ xs) ys = x ∷ append xs ys

normalizeVal : ∀ {Coord : Set} → Coord → DeltaVal → List (UnitDelta Coord)
normalizeVal c dm2 = unit c down ∷ unit c down ∷ []
normalizeVal c dm1 = unit c down ∷ []
normalizeVal c d0  = []
normalizeVal c dp1 = unit c up ∷ []
normalizeVal c dp2 = unit c up ∷ unit c up ∷ []

normalizeEntries : ∀ {Coord : Set} → List (Σ Coord (λ _ → DeltaVal)) → List (UnitDelta Coord)
normalizeEntries [] = []
normalizeEntries ((c , δ) ∷ rest) = append (normalizeVal c δ) (normalizeEntries rest)

applyUnitDeltaWith :
  ∀ {Coord State : Set} →
  (State → Coord → Signed) →
  (State → Coord → Signed → State) →
  State → UnitDelta Coord → State
applyUnitDeltaWith stateAt setAt y u =
  setAt y (coord u) (addSigned (stateAt y (coord u)) (unitDeltaValue (sign u)))

applyUnitDeltasWith :
  ∀ {Coord State : Set} →
  (State → Coord → Signed) →
  (State → Coord → Signed → State) →
  State → List (UnitDelta Coord) → State
applyUnitDeltasWith stateAt setAt y [] = y
applyUnitDeltasWith stateAt setAt y (u ∷ us) =
  applyUnitDeltasWith stateAt setAt (applyUnitDeltaWith stateAt setAt y u) us

record SignedIROps : Set₁ where
  field
    Coord       : Set
    IRState     : Set
    Delta       : Set
    stateAt     : IRState → Coord → Signed
    setAt       : IRState → Coord → Signed → IRState
    deltaEntries : Delta → List (Σ Coord (λ _ → DeltaVal))
    applyDelta  : IRState → Delta → IRState

open SignedIROps public

applyUnitDelta : (I : SignedIROps) → IRState I → UnitDelta (Coord I) → IRState I
applyUnitDelta I = applyUnitDeltaWith (stateAt I) (setAt I)

applyUnitDeltas : (I : SignedIROps) → IRState I → List (UnitDelta (Coord I)) → IRState I
applyUnitDeltas I = applyUnitDeltasWith (stateAt I) (setAt I)

normalize : (I : SignedIROps) → Delta I → List (UnitDelta (Coord I))
normalize I δ = normalizeEntries (deltaEntries I δ)

record NormalizationContract (I : SignedIROps) : Set₁ where
  field
    normalize-sound :
      ∀ y δ →
      applyUnitDeltas I y (normalize I δ) ≡ applyDelta I y δ

open NormalizationContract public

record PrimeExecution (I : SignedIROps) : Set₁ where
  field
    PrimeTag    : Set
    PrimeState  : Set
    Fraction    : Set
    encodeY     : IRState I → PrimeState
    decodeY     : PrimeState → IRState I
    applyFrac   : PrimeState → Fraction → PrimeState
    decode-encode : ∀ y → decodeY (encodeY y) ≡ y
    WellFormedY : PrimeState → Set
    WellFormedFrac : Fraction → Set
    wf-encode   : ∀ y → WellFormedY (encodeY y)
    applyFrac-preserves-wellFormed :
      ∀ {py f} →
      WellFormedY py →
      WellFormedFrac f →
      WellFormedY (applyFrac py f)

open PrimeExecution public

applyFracs : ∀ {I : SignedIROps} → (P : PrimeExecution I) → PrimeState P → List (Fraction P) → PrimeState P
applyFracs P y [] = y
applyFracs P y (f ∷ fs) = applyFracs P (applyFrac P y f) fs

record UnitRealization (I : SignedIROps) (P : PrimeExecution I) : Set₁ where
  field
    realizeUnit :
      IRState I → UnitDelta (Coord I) → Fraction P

    realizeUnit-wellFormed :
      ∀ y u →
      WellFormedFrac P (realizeUnit y u)

    realizeUnit-encode-step :
      ∀ y u →
      applyFrac P (encodeY P y) (realizeUnit y u) ≡
      encodeY P (applyUnitDelta I y u)

open UnitRealization public

realizeNormalized :
  ∀ {I : SignedIROps} →
  (P : PrimeExecution I) →
  (R : UnitRealization I P) →
  IRState I → List (UnitDelta (Coord I)) → List (Fraction P)
realizeNormalized {I} P R y [] = []
realizeNormalized {I} P R y (u ∷ us) =
  realizeUnit R y u ∷ realizeNormalized {I} P R (applyUnitDelta I y u) us

sym : ∀ {A : Set} {x y : A} → x ≡ y → y ≡ x
sym refl = refl

trans : ∀ {A : Set} {x y z : A} → x ≡ y → y ≡ z → x ≡ z
trans refl yz = yz

decodeRealizeNormalized :
  ∀ {I : SignedIROps} →
  (P : PrimeExecution I) →
  (R : UnitRealization I P) →
  ∀ y us →
  decodeY P (applyFracs P (encodeY P y) (realizeNormalized P R y us)) ≡
  applyUnitDeltas I y us
decodeRealizeNormalized {I} P R y [] = decode-encode P y
decodeRealizeNormalized {I} P R y (u ∷ us)
  rewrite realizeUnit-encode-step R y u
  = decodeRealizeNormalized {I} P R (applyUnitDelta I y u) us

realizeUnit-preserves-wellFormed :
  ∀ {I : SignedIROps} →
  (P : PrimeExecution I) →
  (R : UnitRealization I P) →
  ∀ y u →
  WellFormedY P (applyFrac P (encodeY P y) (realizeUnit R y u))
realizeUnit-preserves-wellFormed P R y u =
  applyFrac-preserves-wellFormed P (wf-encode P y) (realizeUnit-wellFormed R y u)

realizeNormalized-preserves-wellFormed :
  ∀ {I : SignedIROps} →
  (P : PrimeExecution I) →
  (R : UnitRealization I P) →
  ∀ y us →
  WellFormedY P (applyFracs P (encodeY P y) (realizeNormalized P R y us))
realizeNormalized-preserves-wellFormed {I} P R y [] = wf-encode P y
realizeNormalized-preserves-wellFormed {I} P R y (u ∷ us)
  rewrite realizeUnit-encode-step R y u
  = realizeNormalized-preserves-wellFormed {I} P R (applyUnitDelta I y u) us

realizeDelta-sound :
  ∀ {I : SignedIROps} →
  (N : NormalizationContract I) →
  (P : PrimeExecution I) →
  (R : UnitRealization I P) →
  ∀ y δ →
  decodeY P
    (applyFracs P
      (encodeY P y)
      (realizeNormalized P R y (normalize I δ)))
  ≡ applyDelta I y δ
realizeDelta-sound {I} N P R y δ =
  trans
    (decodeRealizeNormalized {I} P R y (normalize I δ))
    (normalize-sound N y δ)

realizeDelta-preserves-wellFormed :
  ∀ {I : SignedIROps} →
  (P : PrimeExecution I) →
  (R : UnitRealization I P) →
  ∀ y δ →
  WellFormedY P
    (applyFracs P
      (encodeY P y)
      (realizeNormalized P R y (normalize I δ)))
realizeDelta-preserves-wellFormed {I} P R y δ =
  realizeNormalized-preserves-wellFormed {I} P R y (normalize I δ)

record RegimeValidBridge
  {I : SignedIROps}
  (N : NormalizationContract I)
  (P : PrimeExecution I)
  (R : UnitRealization I P) : Set₁ where
  field
    classifyDelta :
      IRState I → Delta I → RegimeClass

    wellFormed-preserved :
      ∀ y δ →
      WellFormedY P
        (applyFracs P
          (encodeY P y)
          (realizeNormalized P R y (normalize I δ)))

    strict-contraction :
      ∀ y δ →
      StrictContractionWitness (classifyDelta y δ)

    bounded-transmutation :
      ∀ y δ →
      BoundedTransmutationWitness (classifyDelta y δ)

default-wellFormed-preserved :
  ∀ {I : SignedIROps} →
  (P : PrimeExecution I) →
  (R : UnitRealization I P) →
  ∀ y δ →
  WellFormedY P
    (applyFracs P
      (encodeY P y)
      (realizeNormalized P R y (normalize I δ)))
default-wellFormed-preserved {I} P R y δ =
  realizeDelta-preserves-wellFormed {I} P R y δ

bridgeStrictContractionStep :
  ∀ {I : SignedIROps} →
  {N : NormalizationContract I} →
  {P : PrimeExecution I} →
  {R : UnitRealization I P} →
  (B : RegimeValidBridge N P R) →
  ∀ y δ →
  Nat
bridgeStrictContractionStep B y δ =
  strictContractionStepOf (RegimeValidBridge.strict-contraction B y δ)

bridgeTransmutationBound :
  ∀ {I : SignedIROps} →
  {N : NormalizationContract I} →
  {P : PrimeExecution I} →
  {R : UnitRealization I P} →
  (B : RegimeValidBridge N P R) →
  ∀ y δ →
  Nat
bridgeTransmutationBound B y δ =
  transmutationBoundOf (RegimeValidBridge.bounded-transmutation B y δ)
