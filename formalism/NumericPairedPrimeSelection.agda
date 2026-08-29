module formalism.NumericPairedPrimeSelection where

open import Agda.Builtin.Equality using (_≡_; refl)
open import Agda.Builtin.Bool using (Bool; true; false)
open import Agda.Builtin.List using (List; []; _∷_)
open import Agda.Builtin.Unit using (⊤; tt)

import formalism.GenericMacroBridge as G

------------------------------------------------------------------------
-- Numeric paired-prime seam.
--
-- The existing symbolic bridge already knows which PrimeTag is active in each
-- register and already proves that a realized unit fraction replaces exactly
-- the touched register tag.  The external FRACTRAN interpreter instead asks a
-- divisibility question about an integer denominator.
--
-- The one genuinely arithmetic bridge law is therefore:
--
--   denominator(f) divides encodeInt(py)
--        iff
--   the symbolic denominator tag of f is active in py.
--
-- Once a concrete numeric encoding proves this law, FRACTRAN applicability is
-- no longer an independent executable assumption: it is the integer image of
-- the already-owned symbolic active-tag semantics.
------------------------------------------------------------------------

record NumericPairedPrimeInterpretation
    {I : G.SignedIROps}
    (P : G.PrimeExecution I) : Set₁ where
  field
    IntegerState : Set

    encodeInt : G.PrimeExecution.PrimeState P → IntegerState

    denominatorTag :
      G.PrimeExecution.Fraction P →
      G.PrimeExecution.PrimeTag P

    ActiveTag :
      G.PrimeExecution.PrimeState P →
      G.PrimeExecution.PrimeTag P → Set

    DenominatorDivides :
      IntegerState →
      G.PrimeExecution.Fraction P → Set

    divides-implies-active :
      ∀ py f →
      DenominatorDivides (encodeInt py) f →
      ActiveTag py (denominatorTag f)

    active-implies-divides :
      ∀ py f →
      ActiveTag py (denominatorTag f) →
      DenominatorDivides (encodeInt py) f

open NumericPairedPrimeInterpretation public

numericApplies :
  ∀ {I : G.SignedIROps}
    {P : G.PrimeExecution I} →
  NumericPairedPrimeInterpretation P →
  G.PrimeExecution.PrimeState P →
  G.PrimeExecution.Fraction P → Set
numericApplies N py f =
  DenominatorDivides N (encodeInt N py) f

activeTagExactlyNumericApplicability :
  ∀ {I : G.SignedIROps}
    {P : G.PrimeExecution I}
    (N : NumericPairedPrimeInterpretation P)
    (py : G.PrimeExecution.PrimeState P)
    (f : G.PrimeExecution.Fraction P) →
  (numericApplies N py f → ActiveTag N py (denominatorTag N f))
  ×
  (ActiveTag N py (denominatorTag N f) → numericApplies N py f)
activeTagExactlyNumericApplicability N py f =
  divides-implies-active N py f , active-implies-divides N py f

inactiveDenominatorBlocksNumericFraction :
  ∀ {I : G.SignedIROps}
    {P : G.PrimeExecution I}
    (N : NumericPairedPrimeInterpretation P)
    (py : G.PrimeExecution.PrimeState P)
    (f : G.PrimeExecution.Fraction P) →
  (ActiveTag N py (denominatorTag N f) → ⊥) →
  numericApplies N py f → ⊥
inactiveDenominatorBlocksNumericFraction N py f inactive applies =
  inactive (divides-implies-active N py f applies)

activeDenominatorMakesNumericFractionApplicable :
  ∀ {I : G.SignedIROps}
    {P : G.PrimeExecution I}
    (N : NumericPairedPrimeInterpretation P)
    (py : G.PrimeExecution.PrimeState P)
    (f : G.PrimeExecution.Fraction P) →
  ActiveTag N py (denominatorTag N f) →
  numericApplies N py f
activeDenominatorMakesNumericFractionApplicable N py f active =
  active-implies-divides N py f active

------------------------------------------------------------------------
-- Prefix selection receipt.
--
-- This is deliberately phrased in symbolic active-tag vocabulary.  A concrete
-- paired-prime implementation proves previous denominators inactive and the
-- intended denominator active using the symbolic macro state; the two theorems
-- above turn those facts into exact integer divisibility/non-divisibility.
------------------------------------------------------------------------

record NumericIntendedStepReceipt
    {I : G.SignedIROps}
    {P : G.PrimeExecution I}
    (N : NumericPairedPrimeInterpretation P)
    (py : G.PrimeExecution.PrimeState P)
    (earlier : List (G.PrimeExecution.Fraction P))
    (intended : G.PrimeExecution.Fraction P) : Set₁ where
  constructor numeric-intended-step-receipt
  field
    earlierInactive :
      (f : G.PrimeExecution.Fraction P) →
      Member f earlier →
      ActiveTag N py (denominatorTag N f) → ⊥

    intendedActive :
      ActiveTag N py (denominatorTag N intended)

open NumericIntendedStepReceipt public

data Member {A : Set} (x : A) : List A → Set where
  here : ∀ {xs} → Member x (x ∷ xs)
  there : ∀ {y xs} → Member x xs → Member x (y ∷ xs)

receiptBlocksEveryEarlierNumericFraction :
  ∀ {I : G.SignedIROps}
    {P : G.PrimeExecution I}
    {N : NumericPairedPrimeInterpretation P}
    {py : G.PrimeExecution.PrimeState P}
    {earlier : List (G.PrimeExecution.Fraction P)}
    {intended : G.PrimeExecution.Fraction P} →
  NumericIntendedStepReceipt N py earlier intended →
  (f : G.PrimeExecution.Fraction P) →
  Member f earlier →
  numericApplies N py f → ⊥
receiptBlocksEveryEarlierNumericFraction receipt f member applies =
  earlierInactive receipt f member
    (divides-implies-active _ _ _ applies)

receiptMakesIntendedNumericFractionApplicable :
  ∀ {I : G.SignedIROps}
    {P : G.PrimeExecution I}
    {N : NumericPairedPrimeInterpretation P}
    {py : G.PrimeExecution.PrimeState P}
    {earlier : List (G.PrimeExecution.Fraction P)}
    {intended : G.PrimeExecution.Fraction P} →
  NumericIntendedStepReceipt N py earlier intended →
  numericApplies N py intended
receiptMakesIntendedNumericFractionApplicable receipt =
  active-implies-divides _ _ _ (intendedActive receipt)

------------------------------------------------------------------------
-- Trust boundary.
------------------------------------------------------------------------

record NumericPairedPrimeBoundary : Set where
  constructor numericPairedPrimeBoundary
  field
    symbolicRealisationAlreadyOwned : Bool
    symbolicRealisationAlreadyOwnedIsTrue :
      symbolicRealisationAlreadyOwned ≡ true

    numericApplicabilityReducesToActiveTagLaw : Bool
    numericApplicabilityReducesToActiveTagLawIsTrue :
      numericApplicabilityReducesToActiveTagLaw ≡ true

    pythonDivisibilityCheckIsArithmeticProof : Bool
    pythonDivisibilityCheckIsArithmeticProofIsFalse :
      pythonDivisibilityCheckIsArithmeticProof ≡ false

    concretePrimeDivisibilityLawStillRequired : Bool
    concretePrimeDivisibilityLawStillRequiredIsTrue :
      concretePrimeDivisibilityLawStillRequired ≡ true

canonicalNumericPairedPrimeBoundary : NumericPairedPrimeBoundary
canonicalNumericPairedPrimeBoundary =
  numericPairedPrimeBoundary
    true refl
    true refl
    false refl
    true refl

-- Local empty type avoids importing a second logic hierarchy.
data ⊥ : Set where
