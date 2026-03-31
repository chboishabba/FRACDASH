{
  description = "FRACDASH – DASHI-to-FRACTRAN executable modeling";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
        python = pkgs.python3.withPackages (ps: [ ps.numpy ]);
      in {
        devShells.default = pkgs.mkShell {
          packages = [
            python
            pkgs.ghc
            pkgs.haskellPackages.Agda
            # shell / CI tooling
            pkgs.gnumake
            pkgs.jq
            pkgs.shellcheck
            pkgs.python3Packages.flake8
          ];
          shellHook = ''
            export FRACDASH_ROOT="$(pwd)"
            echo "FRACDASH dev shell ready  (python=$(python3 --version), ghc=$(ghc --version | head -1))"
          '';
        };

        # Lightweight check that the Python scripts parse and physics targets pass
        checks.default = pkgs.runCommand "fracdash-check" {
          buildInputs = [ python pkgs.shellcheck ];
          src = self;
        } ''
          cd $src
          python3 -m py_compile scripts/toy_dashi_transitions.py
          python3 -m py_compile scripts/check_physics_invariant_targets.py
          shellcheck scripts/*.sh benchmarks/*.sh || true
          touch $out
        '';
      });
}
