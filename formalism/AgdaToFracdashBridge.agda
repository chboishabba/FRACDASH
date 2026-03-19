module formalism.AgdaToFracdashBridge where

open import Agda.Builtin.Equality using (_≡_; refl)
open import Agda.Builtin.Int using (Int)
open import Agda.Builtin.List using (List; []; _∷_)
open import Agda.Builtin.Nat using (Nat)
open import Agda.Builtin.Sigma using (Σ; _,_)
open import Agda.Builtin.Unit using (⊤; tt)

------------------------------------------------------------------------
-- Local FRACDASH-only scaffold for bridge correctness.
--
-- This file is intentionally not part of ../dashi_agda.
-- It states the minimal formal objects needed for the AGDAS -> FRACDASH
-- executable bridge:
--
-- 1. source transition semantics
-- 2. signed exponent-vector IR
-- 3. FRACTRAN realization of that IR
------------------------------------------------------------------------

record TransitionSystem : Set₁ where
  field
    State : Set
    Step  : State → State → Set

open TransitionSystem public

------------------------------------------------------------------------
-- Source / target packages
------------------------------------------------------------------------

record SourceSemantics : Set₁ where
  field
    X : TransitionSystem

open SourceSemantics public

record PrimeBasis : Set where
  field
    arity : Nat

open PrimeBasis public

record ExpVec (B : PrimeBasis) : Set where
  constructor vec
  field
    exponents : List Int

open ExpVec public

record Delta (B : PrimeBasis) : Set where
  constructor delta
  field
    coords : List Int

open Delta public

record IRSemantics : Set₁ where
  field
    basis     : PrimeBasis
    Z         : TransitionSystem
    applyDelta : State Z → Delta basis → State Z

open IRSemantics public

record TargetSemantics : Set₁ where
  field
    Y : TransitionSystem

open TargetSemantics public

------------------------------------------------------------------------
-- Compiler / abstraction / decoder
------------------------------------------------------------------------

record Compiler
  (S : SourceSemantics)
  (I : IRSemantics)
  (T : TargetSemantics) : Set₁ where
  field
    compile  : State (X S) → State (Z I)
    realize  : State (Z I) → State (Y T)
    decode   : State (Y T) → Set
    observeX : State (X S) → Set

open Compiler public

------------------------------------------------------------------------
-- Refinement and forward simulation
------------------------------------------------------------------------

record Refinement
  (S : SourceSemantics)
  (I : IRSemantics) : Set₁ where
  field
    R : State (X S) → State (Z I) → Set

open Refinement public

record ForwardSimulation
  (S : SourceSemantics)
  (I : IRSemantics)
  (B : Refinement S I) : Set₁ where
  field
    simulate-step :
      ∀ {x x' z} →
      R B x z →
      Step (X S) x x' →
      Σ (State (Z I)) (λ z' → Σ (Step (Z I) z z') (λ _ → R B x' z'))

open ForwardSimulation public

------------------------------------------------------------------------
-- Step-to-delta compilation
------------------------------------------------------------------------

record StepDelta
  (S : SourceSemantics)
  (I : IRSemantics)
  (K : Compiler S I (record { Y = Z I })) : Set₁ where
  field
    deltaOf :
      ∀ {x x'} →
      Step (X S) x x' →
      Delta (basis I)

    delta-correct :
      ∀ {x x'} →
      (sx : Step (X S) x x') →
      compile K x' ≡ applyDelta I (compile K x) (deltaOf sx)

open StepDelta public

------------------------------------------------------------------------
-- FRACTRAN realization of the signed IR
------------------------------------------------------------------------

record FractranRealization
  (I : IRSemantics)
  (T : TargetSemantics) : Set₁ where
  field
    UnitDelta : Set
    Fraction : Set

    encodeZ : State (Z I) → State (Y T)
    decodeY : State (Y T) → State (Z I)

    normalize : Delta (basis I) → List UnitDelta

    realizeUnit : State (Y T) → UnitDelta → List Fraction
    realizeNormalized : State (Y T) → List UnitDelta → List Fraction

    executeFractions :
      State (Y T) → List Fraction → State (Y T)

    sound :
      ∀ (z : State (Z I)) (δ : Delta (basis I)) →
      decodeY
        (executeFractions
          (encodeZ z)
          (realizeNormalized (encodeZ z) (normalize δ)))
      ≡ applyDelta I z δ

open FractranRealization public

------------------------------------------------------------------------
-- Strongest initial refinement relation
------------------------------------------------------------------------

ExactRefinement :
  (S : SourceSemantics) →
  (I : IRSemantics) →
  (K : Compiler S I (record { Y = Z I })) →
  Refinement S I
ExactRefinement S I K = record
  { R = λ x z → compile K x ≡ z
  }

------------------------------------------------------------------------
-- Notes
--
-- This scaffold intentionally leaves several codomains abstract:
-- - decode / observeX currently return Set rather than a fixed observable type
-- - the signed-IR -> FRACTRAN realization is now stated at macro execution
--   level, but concrete paired-prime arithmetic still lives in slice-specific
--   instances rather than this generic scaffold
--
-- The immediate theorem target for FRACDASH is delta-correctness:
--
--   each canonical source step compiles to an exact signed exponent update
--
-- Only after that should the repo lock down the stronger vanilla-FRACTRAN
-- realization theorems for paired-prime or macro-step encodings.
------------------------------------------------------------------------
