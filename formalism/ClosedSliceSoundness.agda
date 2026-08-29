module formalism.ClosedSliceSoundness where

open import Agda.Builtin.Bool using (Bool; true; false)
open import Agda.Builtin.Equality using (_≡_; refl)

------------------------------------------------------------------------
-- BIDI rollup for the currently closed symbolic compiler slices.
--
-- This module adds no new compiler mathematics.  It gives downstream users one
-- stable public surface for the exact source-step -> signed-IR -> symbolic
-- paired-prime target theorems already proved in the historical slice modules.
------------------------------------------------------------------------

open import formalism.GenericMacroBridge public
  using (realizeDelta-sound; realizeDelta-preserves-wellFormed)

open import formalism.Physics1StepDelta public
  using ()
  renaming (realizeNormalized-target-sound to physics1-target-sound)

open import formalism.Physics3StepDelta public
  using ()
  renaming (realizeNormalized-target-sound to physics3-target-sound)

open import formalism.Physics15StepDelta public
  using ()
  renaming (realizeNormalized-target-sound to physics15-target-sound)

open import formalism.Physics19StepDelta public
  using ()
  renaming (realizeNormalized-target-sound to physics19-target-sound)

open import formalism.Physics20StepDelta public
  using ()
  renaming (realizeNormalized-target-sound to physics20-target-sound)

open import formalism.Physics21StepDelta public
  using ()
  renaming (realizeNormalized-target-sound to physics21-target-sound)

open import formalism.Physics22StepDelta public
  using ()
  renaming (realizeNormalized-target-sound to physics22-target-sound)

------------------------------------------------------------------------
-- Claim boundary.
--
-- The re-exported theorems establish exact symbolic macro execution after
-- decoding for the listed source slices.  They do not by themselves establish
-- that an external integer FRACTRAN interpreter implements the symbolic target
-- arithmetic.  That executable/numeric realization remains a distinct receipt.
------------------------------------------------------------------------

record ClosedSliceSoundnessBoundary : Set where
  constructor closedSliceSoundnessBoundary
  field
    physics1SymbolicTargetSound : Bool
    physics1SymbolicTargetSoundIsTrue : physics1SymbolicTargetSound ≡ true

    physics3SymbolicTargetSound : Bool
    physics3SymbolicTargetSoundIsTrue : physics3SymbolicTargetSound ≡ true

    physics15SymbolicTargetSound : Bool
    physics15SymbolicTargetSoundIsTrue : physics15SymbolicTargetSound ≡ true

    physics19SymbolicTargetSound : Bool
    physics19SymbolicTargetSoundIsTrue : physics19SymbolicTargetSound ≡ true

    physics20SymbolicTargetSound : Bool
    physics20SymbolicTargetSoundIsTrue : physics20SymbolicTargetSound ≡ true

    physics21SymbolicTargetSound : Bool
    physics21SymbolicTargetSoundIsTrue : physics21SymbolicTargetSound ≡ true

    physics22SymbolicTargetSound : Bool
    physics22SymbolicTargetSoundIsTrue : physics22SymbolicTargetSound ≡ true

    symbolicMacroSoundnessIsNumericInterpreterSoundness : Bool
    symbolicMacroSoundnessIsNumericInterpreterSoundnessIsFalse :
      symbolicMacroSoundnessIsNumericInterpreterSoundness ≡ false

canonicalClosedSliceSoundnessBoundary : ClosedSliceSoundnessBoundary
canonicalClosedSliceSoundnessBoundary =
  closedSliceSoundnessBoundary
    true refl
    true refl
    true refl
    true refl
    true refl
    true refl
    true refl
    false refl
