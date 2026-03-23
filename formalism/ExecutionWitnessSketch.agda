module formalism.ExecutionWitnessSketch where

open import Agda.Builtin.Unit using (⊤; tt)
open import Agda.Builtin.Sigma using (Σ; _,_)
open import Agda.Builtin.Equality using (_≡_; refl)

import formalism.GenericMacroBridge as G

------------------------------------------------------------------------
-- Executable-side witness sketch
--
-- This is a FRACDASH-local surrogate for the upstream execution-
-- admissibility and family-classification witnesses introduced in
-- `../dashi_agda/DASHI/Physics/Closure/ExecutionAdmissibility*.agda`.
--
-- It is intentionally lightweight: it packages the regime class and a
-- per-state well-formedness predicate alongside a stub for execution
-- admissibility and a finite family tag.
------------------------------------------------------------------------

record ExecutionStatus (Y : Set) : Set₁ where
  field
    regimeClass : G.RegimeClass
    wellFormedY : Y → Set
    executionAdmissible : Set
    familyTag : Set
    evidence : executionAdmissible

open ExecutionStatus public

------------------------------------------------------------------------
-- Helpers
------------------------------------------------------------------------

-- The conservative default bundles the existing regime class plus a
-- well-formedness predicate and treats admissibility as unit evidence.
conservativeDefault :
  ∀ {Y : Set} →
  (wf : Y → Set) →
  ExecutionStatus Y
conservativeDefault wf = record
  { regimeClass = G.conservative-contracting
  ; wellFormedY = wf
  ; executionAdmissible = ⊤
  ; familyTag = ⊤
  ; evidence = tt
  }

-- Given a bounded-transmutation witness, expose its numeric bound as a
-- simple classification surrogate.
familyTagFromBound :
  ∀ {c : G.RegimeClass} →
  G.BoundedTransmutationWitness c →
  Σ G.RegimeClass (λ _ → Set)
familyTagFromBound w =
  (G.transmuting-contracting , G.BoundedTransmutationWitness G.transmuting-contracting)
