module formalism.Physics3StepDelta where

open import Agda.Builtin.Equality using (_≡_; refl)
open import Agda.Builtin.List using (List; []; _∷_)
open import Agda.Builtin.Sigma using (Σ; _,_)
import formalism.GenericMacroBridge as G

------------------------------------------------------------------------
-- Concrete StepDelta instance for the 6-register `physics3` bridge slice.
--
-- This intentionally mirrors the structure of Physics1StepDelta:
--
-- - source states live on the reduced 6-register carrier
-- - source steps are the exported template-level transition constructors
-- - compilation maps directly into a signed 6-register IR
-- - each source step compiles to an exact signed delta
------------------------------------------------------------------------

open G using (Signed; negative; zero; positive; DeltaVal; dm2; dm1; d0; dp1; dp2)

record Physics3State : Set where
  constructor st
  field
    r1 : Signed
    r2 : Signed
    r3 : Signed
    r4 : Signed
    r5 : Signed
    r6 : Signed

open Physics3State public

record Exp6 : Set where
  constructor exp6
  field
    e1 : Signed
    e2 : Signed
    e3 : Signed
    e4 : Signed
    e5 : Signed
    e6 : Signed

open Exp6 public

record Delta6 : Set where
  constructor delta6
  field
    d1 : DeltaVal
    d2 : DeltaVal
    d3 : DeltaVal
    d4 : DeltaVal
    d5 : DeltaVal
    d6 : DeltaVal

open Delta6 public

compile : Physics3State → Exp6
compile (st a b c d e f) = exp6 a b c d e f

infix 20 _↦₃_

data _↦₃_ : Physics3State → Physics3State → Set where
  scan-left-high :
    st negative zero zero zero zero zero ↦₃
    st negative zero zero zero positive zero

  scan-left-mid :
    st positive zero zero zero zero zero ↦₃
    st positive zero zero zero positive zero

  scan-right-high :
    st zero negative zero zero zero zero ↦₃
    st zero negative zero zero negative zero

  scan-right-mid :
    st zero positive zero zero zero zero ↦₃
    st zero positive zero zero negative zero

  join-left-high :
    st negative zero zero zero positive negative ↦₃
    st negative zero negative zero positive negative

  join-right-high :
    st zero negative zero zero negative negative ↦₃
    st zero negative negative zero negative negative

  join-left-mid :
    st positive zero zero zero positive negative ↦₃
    st positive zero positive zero positive positive

  join-right-mid :
    st zero positive zero zero negative negative ↦₃
    st zero positive positive zero negative positive

  contract-high :
    st zero zero negative positive zero negative ↦₃
    st zero zero positive positive zero positive

  contract-mid :
    st zero zero positive positive zero positive ↦₃
    st zero zero zero negative zero zero

  boundary-to-shell :
    st zero zero zero negative zero zero ↦₃
    st zero zero zero zero zero zero

  shell-to-interior :
    st zero zero zero zero zero zero ↦₃
    st zero zero zero positive zero negative

deltaOf : ∀ {x x'} → x ↦₃ x' → Delta6
deltaOf scan-left-high   = delta6 d0 d0 d0 d0 dp1 d0
deltaOf scan-left-mid    = delta6 d0 d0 d0 d0 dp1 d0
deltaOf scan-right-high  = delta6 d0 d0 d0 d0 dm1 d0
deltaOf scan-right-mid   = delta6 d0 d0 d0 d0 dm1 d0
deltaOf join-left-high   = delta6 d0 d0 dm1 d0 d0 d0
deltaOf join-right-high  = delta6 d0 d0 dm1 d0 d0 d0
deltaOf join-left-mid    = delta6 d0 d0 dp1 d0 d0 dp2
deltaOf join-right-mid   = delta6 d0 d0 dp1 d0 d0 dp2
deltaOf contract-high    = delta6 d0 d0 dp2 d0 d0 dp2
deltaOf contract-mid     = delta6 d0 d0 dm1 dm2 d0 dm1
deltaOf boundary-to-shell = delta6 d0 d0 d0 dp1 d0 d0
deltaOf shell-to-interior = delta6 d0 d0 d0 dp1 d0 dm1

------------------------------------------------------------------------
-- Deterministic normalization into unit steps
------------------------------------------------------------------------

data Coord : Set where
  c1 : Coord
  c2 : Coord
  c3 : Coord
  c4 : Coord
  c5 : Coord
  c6 : Coord

deltaEntries6 : Delta6 → List (Σ Coord (λ _ → DeltaVal))
deltaEntries6 (delta6 a b c d e f) =
  (c1 , a) ∷ (c2 , b) ∷ (c3 , c) ∷ (c4 , d) ∷ (c5 , e) ∷ (c6 , f) ∷ []

stateAt : Exp6 → Coord → Signed
stateAt (exp6 a b c d e f) c1 = a
stateAt (exp6 a b c d e f) c2 = b
stateAt (exp6 a b c d e f) c3 = c
stateAt (exp6 a b c d e f) c4 = d
stateAt (exp6 a b c d e f) c5 = e
stateAt (exp6 a b c d e f) c6 = f

setAt : Exp6 → Coord → Signed → Exp6
setAt (exp6 a b c d e f) c1 s = exp6 s b c d e f
setAt (exp6 a b c d e f) c2 s = exp6 a s c d e f
setAt (exp6 a b c d e f) c3 s = exp6 a b s d e f
setAt (exp6 a b c d e f) c4 s = exp6 a b c s e f
setAt (exp6 a b c d e f) c5 s = exp6 a b c d s f
setAt (exp6 a b c d e f) c6 s = exp6 a b c d e s

applyDelta6 : Exp6 → Delta6 → Exp6
applyDelta6 y δ = G.applyUnitDeltasWith stateAt setAt y (G.normalizeEntries (deltaEntries6 δ))

irOps : G.SignedIROps
irOps = record
  { Coord = Coord
  ; IRState = Exp6
  ; Delta = Delta6
  ; stateAt = stateAt
  ; setAt = setAt
  ; deltaEntries = deltaEntries6
  ; applyDelta = applyDelta6
  }

applyUnitDelta : Exp6 → G.UnitDelta Coord → Exp6
applyUnitDelta = G.applyUnitDelta irOps

applyUnitDeltas : Exp6 → List (G.UnitDelta Coord) → Exp6
applyUnitDeltas = G.applyUnitDeltas irOps

normalize : Delta6 → List (G.UnitDelta Coord)
normalize = G.normalize irOps

normalizationContract : G.NormalizationContract irOps
normalizationContract = record
  { normalize-sound = λ y δ → refl
  }

delta-correct : ∀ {x x'} → (sx : x ↦₃ x') → compile x' ≡ applyDelta6 (compile x) (deltaOf sx)
delta-correct scan-left-high = refl
delta-correct scan-left-mid = refl
delta-correct scan-right-high = refl
delta-correct scan-right-mid = refl
delta-correct join-left-high = refl
delta-correct join-right-high = refl
delta-correct join-left-mid = refl
delta-correct join-right-mid = refl
delta-correct contract-high = refl
delta-correct contract-mid = refl
delta-correct boundary-to-shell = refl
delta-correct shell-to-interior = refl

_↦Z_ : Exp6 → Exp6 → Set
z ↦Z z' = Σ Delta6 (λ δ → z' ≡ applyDelta6 z δ)

normalize-correct :
  ∀ {x x'} →
  (sx : x ↦₃ x') →
  compile x' ≡ applyUnitDeltas (compile x) (normalize (deltaOf sx))
normalize-correct scan-left-high = refl
normalize-correct scan-left-mid = refl
normalize-correct scan-right-high = refl
normalize-correct scan-right-mid = refl
normalize-correct join-left-high = refl
normalize-correct join-right-high = refl
normalize-correct join-left-mid = refl
normalize-correct join-right-mid = refl
normalize-correct contract-high = refl
normalize-correct contract-mid = refl
normalize-correct boundary-to-shell = refl
normalize-correct shell-to-interior = refl

------------------------------------------------------------------------
-- Paired-prime target execution layer
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
  p5neg : PrimeTag
  p5zero : PrimeTag
  p5pos : PrimeTag
  p6neg : PrimeTag
  p6zero : PrimeTag
  p6pos : PrimeTag

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
primeOf c5 negative = p5neg
primeOf c5 zero = p5zero
primeOf c5 positive = p5pos
primeOf c6 negative = p6neg
primeOf c6 zero = p6zero
primeOf c6 positive = p6pos

record UnitFraction : Set where
  constructor frac
  field
    touched : Coord
    from : Signed
    to : Signed
    numerator : PrimeTag
    denominator : PrimeTag

open UnitFraction public

applyFraction : Exp6 → UnitFraction → Exp6
applyFraction y f = setAt y (touched f) (to f)

sym : ∀ {A : Set} {x y : A} → x ≡ y → y ≡ x
sym refl = refl

trans : ∀ {A : Set} {x y z : A} → x ≡ y → y ≡ z → x ≡ z
trans refl yz = yz

record PrimeState6 : Set where
  constructor prime6
  field
    q1 : PrimeTag
    q2 : PrimeTag
    q3 : PrimeTag
    q4 : PrimeTag
    q5 : PrimeTag
    q6 : PrimeTag

open PrimeState6 public

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
  f5neg : InFamily c5 p5neg
  f5zero : InFamily c5 p5zero
  f5pos : InFamily c5 p5pos
  f6neg : InFamily c6 p6neg
  f6zero : InFamily c6 p6zero
  f6pos : InFamily c6 p6pos

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
primeOf-family c5 negative = f5neg
primeOf-family c5 zero = f5zero
primeOf-family c5 positive = f5pos
primeOf-family c6 negative = f6neg
primeOf-family c6 zero = f6zero
primeOf-family c6 positive = f6pos

record WellFormedPrimeState6 (py : PrimeState6) : Set where
  constructor wf6
  field
    q1-family : InFamily c1 (q1 py)
    q2-family : InFamily c2 (q2 py)
    q3-family : InFamily c3 (q3 py)
    q4-family : InFamily c4 (q4 py)
    q5-family : InFamily c5 (q5 py)
    q6-family : InFamily c6 (q6 py)

open WellFormedPrimeState6 public

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
decodePrime p5neg = negative
decodePrime p5zero = zero
decodePrime p5pos = positive
decodePrime p6neg = negative
decodePrime p6zero = zero
decodePrime p6pos = positive

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
decodePrimeOf c5 negative = refl
decodePrimeOf c5 zero = refl
decodePrimeOf c5 positive = refl
decodePrimeOf c6 negative = refl
decodePrimeOf c6 zero = refl
decodePrimeOf c6 positive = refl

encodeY : Exp6 → PrimeState6
encodeY (exp6 a b c d e f) =
  prime6
    (primeOf c1 a)
    (primeOf c2 b)
    (primeOf c3 c)
    (primeOf c4 d)
    (primeOf c5 e)
    (primeOf c6 f)

decodeY : PrimeState6 → Exp6
decodeY (prime6 a b c d e f) =
  exp6
    (decodePrime a)
    (decodePrime b)
    (decodePrime c)
    (decodePrime d)
    (decodePrime e)
    (decodePrime f)

decodeEncodeY : ∀ (y : Exp6) → decodeY (encodeY y) ≡ y
decodeEncodeY (exp6 a b c d e f)
  rewrite decodePrimeOf c1 a
        | decodePrimeOf c2 b
        | decodePrimeOf c3 c
        | decodePrimeOf c4 d
        | decodePrimeOf c5 e
        | decodePrimeOf c6 f
  = refl

applyFractionY : PrimeState6 → UnitFraction → PrimeState6
applyFractionY (prime6 a b c d e f) g with touched g
... | c1 = prime6 (numerator g) b c d e f
... | c2 = prime6 a (numerator g) c d e f
... | c3 = prime6 a b (numerator g) d e f
... | c4 = prime6 a b c (numerator g) e f
... | c5 = prime6 a b c d (numerator g) f
... | c6 = prime6 a b c d e (numerator g)

applyFractionY-preserves-wellFormed :
  ∀ {py g} →
  WellFormedPrimeState6 py →
  WellFormedUnitFraction g →
  WellFormedPrimeState6 (applyFractionY py g)
applyFractionY-preserves-wellFormed {py = prime6 a b c d e f} {g = frac c1 from to num den} (wf6 qa qb qc qd qe qf) (wfFrac num-ok den-ok) =
  wf6 num-ok qb qc qd qe qf
applyFractionY-preserves-wellFormed {py = prime6 a b c d e f} {g = frac c2 from to num den} (wf6 qa qb qc qd qe qf) (wfFrac num-ok den-ok) =
  wf6 qa num-ok qc qd qe qf
applyFractionY-preserves-wellFormed {py = prime6 a b c d e f} {g = frac c3 from to num den} (wf6 qa qb qc qd qe qf) (wfFrac num-ok den-ok) =
  wf6 qa qb num-ok qd qe qf
applyFractionY-preserves-wellFormed {py = prime6 a b c d e f} {g = frac c4 from to num den} (wf6 qa qb qc qd qe qf) (wfFrac num-ok den-ok) =
  wf6 qa qb qc num-ok qe qf
applyFractionY-preserves-wellFormed {py = prime6 a b c d e f} {g = frac c5 from to num den} (wf6 qa qb qc qd qe qf) (wfFrac num-ok den-ok) =
  wf6 qa qb qc qd num-ok qf
applyFractionY-preserves-wellFormed {py = prime6 a b c d e f} {g = frac c6 from to num den} (wf6 qa qb qc qd qe qf) (wfFrac num-ok den-ok) =
  wf6 qa qb qc qd qe num-ok

applyFractionsY : PrimeState6 → List UnitFraction → PrimeState6
applyFractionsY y [] = y
applyFractionsY y (g ∷ gs) = applyFractionsY (applyFractionY y g) gs

_↦Y_ : PrimeState6 → PrimeState6 → Set
y ↦Y y' = Σ UnitFraction (λ g → y' ≡ applyFractionY y g)

realizeUnit : Exp6 → G.UnitDelta Coord → UnitFraction
realizeUnit y u =
  let from-state = stateAt y (G.UnitDelta.coord u)
      to-state = G.addSigned from-state (G.unitDeltaValue (G.UnitDelta.sign u))
  in frac (G.UnitDelta.coord u) from-state to-state (primeOf (G.UnitDelta.coord u) to-state) (primeOf (G.UnitDelta.coord u) from-state)

realizeUnit-encode-step :
  ∀ (y : Exp6) (u : G.UnitDelta Coord) →
  applyFractionY (encodeY y) (realizeUnit y u) ≡ encodeY (applyUnitDelta y u)
realizeUnit-encode-step y (G.unit c1 G.up) = refl
realizeUnit-encode-step y (G.unit c1 G.down) = refl
realizeUnit-encode-step y (G.unit c2 G.up) = refl
realizeUnit-encode-step y (G.unit c2 G.down) = refl
realizeUnit-encode-step y (G.unit c3 G.up) = refl
realizeUnit-encode-step y (G.unit c3 G.down) = refl
realizeUnit-encode-step y (G.unit c4 G.up) = refl
realizeUnit-encode-step y (G.unit c4 G.down) = refl
realizeUnit-encode-step y (G.unit c5 G.up) = refl
realizeUnit-encode-step y (G.unit c5 G.down) = refl
realizeUnit-encode-step y (G.unit c6 G.up) = refl
realizeUnit-encode-step y (G.unit c6 G.down) = refl

primeExecution : G.PrimeExecution irOps
primeExecution = record
  { PrimeTag = PrimeTag
  ; PrimeState = PrimeState6
  ; Fraction = UnitFraction
  ; encodeY = encodeY
  ; decodeY = decodeY
  ; applyFrac = applyFractionY
  ; decode-encode = decodeEncodeY
  ; WellFormedY = WellFormedPrimeState6
  ; WellFormedFrac = WellFormedUnitFraction
  ; wf-encode = λ { (exp6 a b c d e f) → wf6 (primeOf-family c1 a) (primeOf-family c2 b) (primeOf-family c3 c) (primeOf-family c4 d) (primeOf-family c5 e) (primeOf-family c6 f) }
  ; applyFrac-preserves-wellFormed = applyFractionY-preserves-wellFormed
  }

unitRealization : G.UnitRealization irOps primeExecution
unitRealization = record
  { realizeUnit = realizeUnit
  ; realizeUnit-wellFormed = λ y u → wfFrac (primeOf-family (G.UnitDelta.coord u) (G.addSigned (stateAt y (G.UnitDelta.coord u)) (G.unitDeltaValue (G.UnitDelta.sign u))))
                                    (primeOf-family (G.UnitDelta.coord u) (stateAt y (G.UnitDelta.coord u)))
  ; realizeUnit-encode-step = realizeUnit-encode-step
  }

realizeNormalized : Exp6 → List (G.UnitDelta Coord) → List UnitFraction
realizeNormalized = G.realizeNormalized primeExecution unitRealization

realizeNormalized-sound :
  ∀ {x x'} →
  (sx : x ↦₃ x') →
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
  (sx : x ↦₃ x') →
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

record RegimeWitness {x x'} (sx : x ↦₃ x') : Set where
  constructor regime-witness
  field
    class : G.RegimeClass
    contracting : StrictlyContracting
    transmutation : BoundedTransmutation class
    wellFormed-target :
      WellFormedPrimeState6
        (G.applyFracs primeExecution
          (encodeY (compile x))
          (realizeNormalized (compile x) (normalize (deltaOf sx))))

physics3-regime-valid : ∀ {x x'} (sx : x ↦₃ x') → RegimeWitness sx
physics3-regime-valid {x = x} scan-left-high =
  regime-witness G.conservative-contracting strictly-contracting conservative-bound
    (G.realizeDelta-preserves-wellFormed primeExecution unitRealization (compile x) (deltaOf scan-left-high))
physics3-regime-valid {x = x} scan-left-mid =
  regime-witness G.conservative-contracting strictly-contracting conservative-bound
    (G.realizeDelta-preserves-wellFormed primeExecution unitRealization (compile x) (deltaOf scan-left-mid))
physics3-regime-valid {x = x} scan-right-high =
  regime-witness G.conservative-contracting strictly-contracting conservative-bound
    (G.realizeDelta-preserves-wellFormed primeExecution unitRealization (compile x) (deltaOf scan-right-high))
physics3-regime-valid {x = x} scan-right-mid =
  regime-witness G.conservative-contracting strictly-contracting conservative-bound
    (G.realizeDelta-preserves-wellFormed primeExecution unitRealization (compile x) (deltaOf scan-right-mid))
physics3-regime-valid {x = x} join-left-high =
  regime-witness G.conservative-contracting strictly-contracting conservative-bound
    (G.realizeDelta-preserves-wellFormed primeExecution unitRealization (compile x) (deltaOf join-left-high))
physics3-regime-valid {x = x} join-right-high =
  regime-witness G.conservative-contracting strictly-contracting conservative-bound
    (G.realizeDelta-preserves-wellFormed primeExecution unitRealization (compile x) (deltaOf join-right-high))
physics3-regime-valid {x = x} join-left-mid =
  regime-witness G.conservative-contracting strictly-contracting conservative-bound
    (G.realizeDelta-preserves-wellFormed primeExecution unitRealization (compile x) (deltaOf join-left-mid))
physics3-regime-valid {x = x} join-right-mid =
  regime-witness G.conservative-contracting strictly-contracting conservative-bound
    (G.realizeDelta-preserves-wellFormed primeExecution unitRealization (compile x) (deltaOf join-right-mid))
physics3-regime-valid {x = x} contract-high =
  regime-witness G.conservative-contracting strictly-contracting conservative-bound
    (G.realizeDelta-preserves-wellFormed primeExecution unitRealization (compile x) (deltaOf contract-high))
physics3-regime-valid {x = x} contract-mid =
  regime-witness G.conservative-contracting strictly-contracting conservative-bound
    (G.realizeDelta-preserves-wellFormed primeExecution unitRealization (compile x) (deltaOf contract-mid))
physics3-regime-valid {x = x} boundary-to-shell =
  regime-witness G.conservative-contracting strictly-contracting conservative-bound
    (G.realizeDelta-preserves-wellFormed primeExecution unitRealization (compile x) (deltaOf boundary-to-shell))
physics3-regime-valid {x = x} shell-to-interior =
  regime-witness G.conservative-contracting strictly-contracting conservative-bound
    (G.realizeDelta-preserves-wellFormed primeExecution unitRealization (compile x) (deltaOf shell-to-interior))
