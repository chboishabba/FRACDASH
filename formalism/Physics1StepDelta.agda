module formalism.Physics1StepDelta where

open import Agda.Builtin.Equality using (_≡_; refl)
open import Agda.Builtin.List using (List; []; _∷_)
open import Agda.Builtin.Sigma using (Σ; _,_)
import formalism.GenericMacroBridge as G

------------------------------------------------------------------------
-- First concrete StepDelta instance for the local FRACDASH bridge.
--
-- This models the `physics1` template slice from `scripts/agdas_bridge.py`
-- directly at the signed-delta IR level:
--
-- - source states live on the 4-register physics1 carrier
-- - source steps are the template-level transition constructors
-- - compilation maps states into a signed exponent-vector sketch
-- - each source step compiles to an exact signed delta
------------------------------------------------------------------------

open G using (Signed; negative; zero; positive; DeltaVal; dm2; dm1; d0; dp1; dp2)

record Physics1State : Set where
  constructor st
  field
    r1 : Signed
    r2 : Signed
    r3 : Signed
    r4 : Signed

open Physics1State public

record Exp4 : Set where
  constructor exp4
  field
    e1 : Signed
    e2 : Signed
    e3 : Signed
    e4 : Signed

open Exp4 public

record Delta4 : Set where
  constructor delta4
  field
    d1 : DeltaVal
    d2 : DeltaVal
    d3 : DeltaVal
    d4 : DeltaVal

open Delta4 public

compile : Physics1State → Exp4
compile (st a b c d) = exp4 a b c d

infix 20 _↦₁_

data _↦₁_ : Physics1State → Physics1State → Set where
  join-left-high :
    ∀ {r2 r4} →
    st negative r2 zero r4 ↦₁ st negative r2 negative r4

  join-right-high :
    ∀ {r1 r4} →
    st r1 negative zero r4 ↦₁ st r1 negative negative r4

  join-left-mid :
    ∀ {r2 r4} →
    st positive r2 zero r4 ↦₁ st positive r2 positive r4

  join-right-mid :
    ∀ {r1 r4} →
    st r1 positive zero r4 ↦₁ st r1 positive positive r4

  contract-high :
    ∀ {r1 r2} →
    st r1 r2 negative positive ↦₁ st r1 r2 positive positive

  contract-mid :
    ∀ {r1 r2} →
    st r1 r2 positive positive ↦₁ st r1 r2 zero negative

  boundary-reset :
    ∀ {r1 r2 r3} →
    st r1 r2 r3 negative ↦₁ st r1 r2 r3 positive

deltaOf : ∀ {x x'} → x ↦₁ x' → Delta4
deltaOf join-left-high  = delta4 d0 d0 dm1 d0
deltaOf join-right-high = delta4 d0 d0 dm1 d0
deltaOf join-left-mid   = delta4 d0 d0 dp1 d0
deltaOf join-right-mid  = delta4 d0 d0 dp1 d0
deltaOf contract-high   = delta4 d0 d0 dp2 d0
deltaOf contract-mid    = delta4 d0 d0 dm1 dm2
deltaOf boundary-reset  = delta4 d0 d0 d0 dp2

------------------------------------------------------------------------
-- Deterministic normalization into unit steps
------------------------------------------------------------------------

data Coord : Set where
  c1 : Coord
  c2 : Coord
  c3 : Coord
  c4 : Coord

deltaEntries4 : Delta4 → List (Σ Coord (λ _ → DeltaVal))
deltaEntries4 (delta4 a b c d) = (c1 , a) ∷ (c2 , b) ∷ (c3 , c) ∷ (c4 , d) ∷ []

stateAt : Exp4 → Coord → Signed
stateAt (exp4 a b c d) c1 = a
stateAt (exp4 a b c d) c2 = b
stateAt (exp4 a b c d) c3 = c
stateAt (exp4 a b c d) c4 = d

setAt : Exp4 → Coord → Signed → Exp4
setAt (exp4 a b c d) c1 s = exp4 s b c d
setAt (exp4 a b c d) c2 s = exp4 a s c d
setAt (exp4 a b c d) c3 s = exp4 a b s d
setAt (exp4 a b c d) c4 s = exp4 a b c s

applyDelta4 : Exp4 → Delta4 → Exp4
applyDelta4 y δ = G.applyUnitDeltasWith stateAt setAt y (G.normalizeEntries (deltaEntries4 δ))

irOps : G.SignedIROps
irOps = record
  { Coord = Coord
  ; IRState = Exp4
  ; Delta = Delta4
  ; stateAt = stateAt
  ; setAt = setAt
  ; deltaEntries = deltaEntries4
  ; applyDelta = applyDelta4
  }

applyUnitDelta : Exp4 → G.UnitDelta Coord → Exp4
applyUnitDelta = G.applyUnitDelta irOps

applyUnitDeltas : Exp4 → List (G.UnitDelta Coord) → Exp4
applyUnitDeltas = G.applyUnitDeltas irOps

normalize : Delta4 → List (G.UnitDelta Coord)
normalize = G.normalize irOps

normalizationContract : G.NormalizationContract irOps
normalizationContract = record
  { normalize-sound = λ y δ → refl
  }

delta-correct : ∀ {x x'} → (sx : x ↦₁ x') → compile x' ≡ applyDelta4 (compile x) (deltaOf sx)
delta-correct join-left-high  = refl
delta-correct join-right-high = refl
delta-correct join-left-mid   = refl
delta-correct join-right-mid  = refl
delta-correct contract-high   = refl
delta-correct contract-mid    = refl
delta-correct boundary-reset  = refl

_↦Z_ : Exp4 → Exp4 → Set
z ↦Z z' = Σ Delta4 (λ δ → z' ≡ applyDelta4 z δ)

normalize-correct :
  ∀ {x x'} →
  (sx : x ↦₁ x') →
  compile x' ≡ applyUnitDeltas (compile x) (normalize (deltaOf sx))
normalize-correct join-left-high = refl
normalize-correct join-right-high = refl
normalize-correct join-left-mid = refl
normalize-correct join-right-mid = refl
normalize-correct contract-high = refl
normalize-correct contract-mid = refl
normalize-correct boundary-reset = refl

------------------------------------------------------------------------
-- Symbolic paired-prime macro realization
------------------------------------------------------------------------

data PrimeTag : Set where
  p1neg : PrimeTag
  p1zero : PrimeTag
  p1pos : PrimeTag
  p2neg : PrimeTag
  p2zero : PrimeTag
  p2pos : PrimeTag
  p3neg : PrimeTag
  p3zero : PrimeTag
  p3pos : PrimeTag
  p4neg : PrimeTag
  p4zero : PrimeTag
  p4pos : PrimeTag

primeOf : Coord → Signed → PrimeTag
primeOf c1 negative = p1neg
primeOf c1 zero = p1zero
primeOf c1 positive = p1pos
primeOf c2 negative = p2neg
primeOf c2 zero = p2zero
primeOf c2 positive = p2pos
primeOf c3 negative = p3neg
primeOf c3 zero = p3zero
primeOf c3 positive = p3pos
primeOf c4 negative = p4neg
primeOf c4 zero = p4zero
primeOf c4 positive = p4pos

record UnitFraction : Set where
  constructor frac
  field
    touched : Coord
    from : Signed
    to : Signed
    numerator : PrimeTag
    denominator : PrimeTag

open UnitFraction public

applyFraction : Exp4 → UnitFraction → Exp4
applyFraction y f = setAt y (touched f) (to f)

sym : ∀ {A : Set} {x y : A} → x ≡ y → y ≡ x
sym refl = refl

trans : ∀ {A : Set} {x y z : A} → x ≡ y → y ≡ z → x ≡ z
trans refl yz = yz

record PrimeState4 : Set where
  constructor prime4
  field
    q1 : PrimeTag
    q2 : PrimeTag
    q3 : PrimeTag
    q4 : PrimeTag

open PrimeState4 public

data InFamily : Coord → PrimeTag → Set where
  f1neg : InFamily c1 p1neg
  f1zero : InFamily c1 p1zero
  f1pos : InFamily c1 p1pos
  f2neg : InFamily c2 p2neg
  f2zero : InFamily c2 p2zero
  f2pos : InFamily c2 p2pos
  f3neg : InFamily c3 p3neg
  f3zero : InFamily c3 p3zero
  f3pos : InFamily c3 p3pos
  f4neg : InFamily c4 p4neg
  f4zero : InFamily c4 p4zero
  f4pos : InFamily c4 p4pos

primeOf-family : ∀ (c : Coord) (s : Signed) → InFamily c (primeOf c s)
primeOf-family c1 negative = f1neg
primeOf-family c1 zero = f1zero
primeOf-family c1 positive = f1pos
primeOf-family c2 negative = f2neg
primeOf-family c2 zero = f2zero
primeOf-family c2 positive = f2pos
primeOf-family c3 negative = f3neg
primeOf-family c3 zero = f3zero
primeOf-family c3 positive = f3pos
primeOf-family c4 negative = f4neg
primeOf-family c4 zero = f4zero
primeOf-family c4 positive = f4pos

record WellFormedPrimeState4 (py : PrimeState4) : Set where
  constructor wf4
  field
    q1-family : InFamily c1 (q1 py)
    q2-family : InFamily c2 (q2 py)
    q3-family : InFamily c3 (q3 py)
    q4-family : InFamily c4 (q4 py)

open WellFormedPrimeState4 public

record WellFormedUnitFraction (f : UnitFraction) : Set where
  constructor wfFrac
  field
    numerator-family : InFamily (touched f) (numerator f)
    denominator-family : InFamily (touched f) (denominator f)

open WellFormedUnitFraction public

decodePrime : PrimeTag → Signed
decodePrime p1neg = negative
decodePrime p1zero = zero
decodePrime p1pos = positive
decodePrime p2neg = negative
decodePrime p2zero = zero
decodePrime p2pos = positive
decodePrime p3neg = negative
decodePrime p3zero = zero
decodePrime p3pos = positive
decodePrime p4neg = negative
decodePrime p4zero = zero
decodePrime p4pos = positive

decodePrimeOf : ∀ (c : Coord) (s : Signed) → decodePrime (primeOf c s) ≡ s
decodePrimeOf c1 negative = refl
decodePrimeOf c1 zero = refl
decodePrimeOf c1 positive = refl
decodePrimeOf c2 negative = refl
decodePrimeOf c2 zero = refl
decodePrimeOf c2 positive = refl
decodePrimeOf c3 negative = refl
decodePrimeOf c3 zero = refl
decodePrimeOf c3 positive = refl
decodePrimeOf c4 negative = refl
decodePrimeOf c4 zero = refl
decodePrimeOf c4 positive = refl

encodeY : Exp4 → PrimeState4
encodeY (exp4 a b c d) = prime4 (primeOf c1 a) (primeOf c2 b) (primeOf c3 c) (primeOf c4 d)

decodeY : PrimeState4 → Exp4
decodeY (prime4 a b c d) = exp4 (decodePrime a) (decodePrime b) (decodePrime c) (decodePrime d)

decodeEncodeY : ∀ (y : Exp4) → decodeY (encodeY y) ≡ y
decodeEncodeY (exp4 a b c d)
  rewrite decodePrimeOf c1 a
        | decodePrimeOf c2 b
        | decodePrimeOf c3 c
        | decodePrimeOf c4 d
  = refl

applyFractionY : PrimeState4 → UnitFraction → PrimeState4
applyFractionY (prime4 a b c d) f with touched f
... | c1 = prime4 (numerator f) b c d
... | c2 = prime4 a (numerator f) c d
... | c3 = prime4 a b (numerator f) d
... | c4 = prime4 a b c (numerator f)

applyFractionY-preserves-wellFormed :
  ∀ {py f} →
  WellFormedPrimeState4 py →
  WellFormedUnitFraction f →
  WellFormedPrimeState4 (applyFractionY py f)
applyFractionY-preserves-wellFormed {py = prime4 a b c d} {f = frac c1 from to num den} (wf4 qa qb qc qd) (wfFrac num-ok den-ok) =
  wf4 num-ok qb qc qd
applyFractionY-preserves-wellFormed {py = prime4 a b c d} {f = frac c2 from to num den} (wf4 qa qb qc qd) (wfFrac num-ok den-ok) =
  wf4 qa num-ok qc qd
applyFractionY-preserves-wellFormed {py = prime4 a b c d} {f = frac c3 from to num den} (wf4 qa qb qc qd) (wfFrac num-ok den-ok) =
  wf4 qa qb num-ok qd
applyFractionY-preserves-wellFormed {py = prime4 a b c d} {f = frac c4 from to num den} (wf4 qa qb qc qd) (wfFrac num-ok den-ok) =
  wf4 qa qb qc num-ok

applyFractionsY : PrimeState4 → List UnitFraction → PrimeState4
applyFractionsY y [] = y
applyFractionsY y (f ∷ fs) = applyFractionsY (applyFractionY y f) fs

_↦Y_ : PrimeState4 → PrimeState4 → Set
y ↦Y y' = Σ UnitFraction (λ f → y' ≡ applyFractionY y f)

realizeUnit : Exp4 → G.UnitDelta Coord → UnitFraction
realizeUnit y u =
  let from-state = stateAt y (G.UnitDelta.coord u)
      to-state = G.addSigned from-state (G.unitDeltaValue (G.UnitDelta.sign u))
  in frac (G.UnitDelta.coord u) from-state to-state (primeOf (G.UnitDelta.coord u) to-state) (primeOf (G.UnitDelta.coord u) from-state)

realizeUnit-encode-step :
  ∀ (y : Exp4) (u : G.UnitDelta Coord) →
  applyFractionY (encodeY y) (realizeUnit y u) ≡ encodeY (applyUnitDelta y u)
realizeUnit-encode-step y (G.unit c1 G.up) = refl
realizeUnit-encode-step y (G.unit c1 G.down) = refl
realizeUnit-encode-step y (G.unit c2 G.up) = refl
realizeUnit-encode-step y (G.unit c2 G.down) = refl
realizeUnit-encode-step y (G.unit c3 G.up) = refl
realizeUnit-encode-step y (G.unit c3 G.down) = refl
realizeUnit-encode-step y (G.unit c4 G.up) = refl
realizeUnit-encode-step y (G.unit c4 G.down) = refl

primeExecution : G.PrimeExecution irOps
primeExecution = record
  { PrimeTag = PrimeTag
  ; PrimeState = PrimeState4
  ; Fraction = UnitFraction
  ; encodeY = encodeY
  ; decodeY = decodeY
  ; applyFrac = applyFractionY
  ; decode-encode = decodeEncodeY
  ; WellFormedY = WellFormedPrimeState4
  ; WellFormedFrac = WellFormedUnitFraction
  ; wf-encode = λ { (exp4 a b c d) → wf4 (primeOf-family c1 a) (primeOf-family c2 b) (primeOf-family c3 c) (primeOf-family c4 d) }
  ; applyFrac-preserves-wellFormed = applyFractionY-preserves-wellFormed
  }

unitRealization : G.UnitRealization irOps primeExecution
unitRealization = record
  { realizeUnit = realizeUnit
  ; realizeUnit-wellFormed = λ y u → wfFrac (primeOf-family (G.UnitDelta.coord u) (G.addSigned (stateAt y (G.UnitDelta.coord u)) (G.unitDeltaValue (G.UnitDelta.sign u))))
                                    (primeOf-family (G.UnitDelta.coord u) (stateAt y (G.UnitDelta.coord u)))
  ; realizeUnit-encode-step = realizeUnit-encode-step
  }

realizeNormalized : Exp4 → List (G.UnitDelta Coord) → List UnitFraction
realizeNormalized = G.realizeNormalized primeExecution unitRealization

realizeNormalized-sound :
  ∀ {x x'} →
  (sx : x ↦₁ x') →
  compile x' ≡
    decodeY
      (G.applyFracs primeExecution
        (encodeY (compile x))
        (realizeNormalized (compile x) (normalize (deltaOf sx))))
realizeNormalized-sound {x = x} sx =
  trans
    (delta-correct sx)
    (sym (G.realizeDelta-sound normalizationContract primeExecution unitRealization (compile x) (deltaOf sx)))

realizeNormalized-target-sound :
  ∀ {x x'} →
  (sx : x ↦₁ x') →
  compile x' ≡
    decodeY
      (G.applyFracs primeExecution
        (encodeY (compile x))
        (realizeNormalized (compile x) (normalize (deltaOf sx))))
realizeNormalized-target-sound {x = x} sx =
  realizeNormalized-sound {x = x} sx

------------------------------------------------------------------------
-- Local conservative regime witness
------------------------------------------------------------------------

data StrictlyContracting : Set where
  strictly-contracting : StrictlyContracting

data BoundedTransmutation : G.RegimeClass → Set where
  conservative-bound : BoundedTransmutation G.conservative-contracting

record RegimeWitness {x x'} (sx : x ↦₁ x') : Set where
  constructor regime-witness
  field
    class : G.RegimeClass
    contracting : StrictlyContracting
    transmutation : BoundedTransmutation class
    wellFormed-target :
      WellFormedPrimeState4
        (G.applyFracs primeExecution
          (encodeY (compile x))
          (realizeNormalized (compile x) (normalize (deltaOf sx))))

physics1-regime-valid : ∀ {x x'} (sx : x ↦₁ x') → RegimeWitness sx
physics1-regime-valid {x = x} sx@join-left-high =
  regime-witness G.conservative-contracting strictly-contracting conservative-bound
    (G.realizeDelta-preserves-wellFormed primeExecution unitRealization (compile x) (deltaOf sx))
physics1-regime-valid {x = x} sx@join-right-high =
  regime-witness G.conservative-contracting strictly-contracting conservative-bound
    (G.realizeDelta-preserves-wellFormed primeExecution unitRealization (compile x) (deltaOf sx))
physics1-regime-valid {x = x} sx@join-left-mid =
  regime-witness G.conservative-contracting strictly-contracting conservative-bound
    (G.realizeDelta-preserves-wellFormed primeExecution unitRealization (compile x) (deltaOf sx))
physics1-regime-valid {x = x} sx@join-right-mid =
  regime-witness G.conservative-contracting strictly-contracting conservative-bound
    (G.realizeDelta-preserves-wellFormed primeExecution unitRealization (compile x) (deltaOf sx))
physics1-regime-valid {x = x} sx@contract-high =
  regime-witness G.conservative-contracting strictly-contracting conservative-bound
    (G.realizeDelta-preserves-wellFormed primeExecution unitRealization (compile x) (deltaOf sx))
physics1-regime-valid {x = x} sx@contract-mid =
  regime-witness G.conservative-contracting strictly-contracting conservative-bound
    (G.realizeDelta-preserves-wellFormed primeExecution unitRealization (compile x) (deltaOf sx))
physics1-regime-valid {x = x} sx@boundary-reset =
  regime-witness G.conservative-contracting strictly-contracting conservative-bound
    (G.realizeDelta-preserves-wellFormed primeExecution unitRealization (compile x) (deltaOf sx))

------------------------------------------------------------------------
-- Notes
--
-- 1. This file now covers three layers for the `physics1` slice:
--    exact signed-delta compilation, deterministic normalization into unit
--    steps, and a paired-prime target execution layer.
-- 2. The local `Y` layer is explicit: target states are concrete per-register
--    prime tags, and decoding target execution back into the signed IR is
--    exact on the `physics1` slice.
-- 3. The concrete numeric FRACTRAN ordering and arithmetic soundness now live
--    in Python artifact checks, where the ordered prime-swap macros are
--    validated against integer execution.
-- 4. Later physics carriers can reuse the same pattern, but may need a weaker
--    refinement relation once template compression or macro-step execution
--    becomes unavoidable.
------------------------------------------------------------------------
