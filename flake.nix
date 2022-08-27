{
  description = "A REST API for managing a MPV instance over via a RPC socket";

  inputs.flake-utils.url = "github:numtide/flake-utils";
  inputs.nixpkgs.url = "github:NixOS/nixpkgs";
  inputs.poetry2nix.url = "github:nix-community/poetry2nix";

  outputs = { self, nixpkgs, flake-utils, poetry2nix }:
    {
      # Nixpkgs overlay providing the application
      overlay = nixpkgs.lib.composeManyExtensions [
        poetry2nix.overlay
        (final: prev: {
          # The application
          grzegorz = prev.poetry2nix.mkPoetryApplication {
            projectDir = ./.;
          };
        })
      ];
    } // (flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = import nixpkgs {
          inherit system;
          overlays = [ self.overlay ];
        };
        entrypoint = pkgs.writeShellApplication {
          name = "grzegorz-run";
          runtimeInputs = [
            pkgs.grzegorz
            pkgs.mpv
          ];
          text = ''
            SPIS_MEG=()
            if test -z "$*"; then
              >&2 echo "DEBUG: No args provided, running with defaults...."
              SPIS_MEG=("--host" "::" "--port" "8080")
            fi
            (
                set -x
                sanic grzegorz.app "''${SPIS_MEG[@]}" "$@"
            )
          '';
        };
      in {
        packages = {
          inherit (pkgs) grzegorz;
          grzegorz-run = entrypoint;
        };

        apps = {
          default.type = "app";
          default.program = "${entrypoint}/bin/grzegorz-run";
        };
      }));
}
