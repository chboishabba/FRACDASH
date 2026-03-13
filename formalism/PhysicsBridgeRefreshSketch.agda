module PhysicsBridgeRefreshSketch where

open import Agda.Builtin.Nat using (Nat)
open import Agda.Builtin.Equality using (_≡_; refl)

------------------------------------------------------------------------
-- Local FRACDASH-only formalism sketch.
--
-- This file is intentionally NOT part of ../dashi_agda.
-- Its purpose is to pin down the executable bridge seam we want before any
-- upstream formalization attempt.
------------------------------------------------------------------------

data Level : Set where
  low  : Level
  mid  : Level
  high : Level

data Flag : Set where
  interior : Flag
  boundary : Flag

record BridgeState : Set where
  constructor st
  field
    leftCode   : Level
    rightCode  : Level
    joinedCode : Level
    regionFlag : Flag

open BridgeState public

------------------------------------------------------------------------
-- Severity join sketch (UFTC-style seam)

joinLevel : Level → Level → Level
joinLevel low  x    = x
joinLevel x    low  = x
joinLevel mid  mid  = mid
joinLevel mid  high = high
joinLevel high mid  = high
joinLevel high high = high

refreshJoin : BridgeState → BridgeState
refreshJoin s =
  st (leftCode s) (rightCode s) (joinLevel (leftCode s) (rightCode s)) (regionFlag s)

------------------------------------------------------------------------
-- Contraction-style relaxation sketch

relax : BridgeState → BridgeState
relax (st l r high interior) = st l r mid interior
relax (st l r mid  interior) = st l r low boundary
relax s = s

------------------------------------------------------------------------
-- Boundary reset sketch

resetBoundary : BridgeState → BridgeState
resetBoundary (st l r j boundary) = st l r j interior
resetBoundary s = s

------------------------------------------------------------------------
-- Intended executable reading
--
-- 1. refreshJoin materializes the current effective severity
-- 2. relax models contraction / descent in the interior
-- 3. resetBoundary re-arms the local environment for another step
--
-- FRACDASH encodes these as explicit FRACTRAN transitions rather than trying
-- to extract them automatically from the upstream AGDA corpus.
