{
  description = "A REST API for managing a MPV instance over via a RPC socket";

  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";

  inputs.fix-python.url = "github:GuillaumeDesforges/fix-python";
  inputs.fix-python.inputs.nixpkgs.follows = "nixpkgs";
  #inputs.fix-python.inputs.flake-utils.follows = "flake-utils";

  outputs = {
    self,
    nixpkgs,
    fix-python,
    ...
  } @ inputs:
  let
    forSystems = systems: f: nixpkgs.lib.genAttrs systems (system: f rec {
      inherit system;
      pkgs = nixpkgs.legacyPackages.${system};
      lib  = nixpkgs.legacyPackages.${system}.lib;
    });
    forAllSystems = forSystems [
      "x86_64-linux"
      "aarch64-linux"
      #"riscv64-linux"
    ];
  in {

    packages = forAllSystems ({ system, pkgs, ...}: rec {
      sanic-ext = with pkgs.python3.pkgs; buildPythonPackage rec {
        pname = "sanic-ext";
        version = "23.12.0";
        src = fetchPypi {
          inherit pname version;
          hash = "sha256-QvxB5/r6WPO3kPaF892KjeKBRgtBadDpH04RuHR/hFw=";
        };
        propagatedBuildInputs = [ pyyaml ];
        doCheck = false;
      };
      grzegorz = with pkgs.python3.pkgs; buildPythonPackage {
        pname = "grzegorz";
        version = (builtins.fromTOML (builtins.readFile ./pyproject.toml)).tool.poetry.version;
        format = "pyproject";
        src = ./.;
        postInstall = ''
        '';
        nativeBuildInputs = [ poetry-core ];
        propagatedBuildInputs = [ setuptools sanic sanic-ext yt-dlp mpv ];
        doCheck = false;
      };
      grzegorz-run = pkgs.writeShellApplication {
        name = "grzegorz-run";
        runtimeInputs = [ (pkgs.python3.withPackages (ps: [ grzegorz ]))  pkgs.mpv ];
        text = ''
          TOOMANYARGS=()
          if test -z "$*"; then
            >&2 echo "DEBUG: No args provided, running with defaults...."
            TOOMANYARGS=("--host" "::" "--port" "8080")
          fi
          (
              set -x
              sanic grzegorz.app "''${TOOMANYARGS[@]}" "$@"
          )
        '';
      };
      default = grzegorz;
    });

    apps = forAllSystems ({ system, pkgs, ...}: {
      default.type = "app";
      default.program = "${self.packages.${system}.grzegorz-run}/bin/grzegorz-run";
    });

    devShells = forAllSystems ({ system, pkgs, ...}: rec {
      default = pkgs.mkShellNoCC {
        packages = with pkgs; [
          poetry
          python3
          # mpv # myust be in sync with system glibc
          fix-python.packages.${system}.default
        ];
        shellHook = let
          inherit (pkgs) lib;
          libs = [
            pkgs.stdenv.cc.cc.lib # dlopen libstdc++
            #pkgs.glibc
            #pkgs.zlib
          ];
          addPath = var: paths: subdir: ''
            export ${var}=${lib.makeSearchPath subdir libs}"''${${var}:+:$${var}}"
          '';
        in ''
          export NIX_PATH=nixpkgs=${nixpkgs}"''${NIX_PATH:+:$NIX_PATH}"
          ${addPath "CPATH"           libs "include"}
          ${addPath "LD_LIBRARY_PATH" libs "lib"}
        '';
      };
    });

    nixosModules.grzegorz-kiosk = { config, pkgs, ... }: let
      inherit (pkgs) lib;
      cfg = config.services.grzegorz;
    in {
      options.services.grzegorz = {

        enable = lib.mkEnableOption (lib.mdDoc "grzegorz");

        package = lib.mkPackageOption self.packages.${config.nixpkgs.system} "grzegorz-run" { };

        listenAddr = lib.mkOption {
            type = lib.types.str;
            default = "::";
        };
        listenPort = lib.mkOption {
            type = lib.types.port;
            default = 9090;
        };
      };
      config = {
        services.cage.enable = true;
        services.cage.program = pkgs.writeShellScript "grzegorz-kiosk" ''
          cd $(mktemp -d)
          ${(lib.escapeShellArgs [
            "${cfg.package}/bin/grzegorz-run"
            "--host" cfg.listenAddr
            "--port" cfg.listenPort
          ])}
        '';
        services.cage.user = "grzegorz";
        users.users."grzegorz".isNormalUser = true;
        system.activationScripts = {
          base-dirs = {
            text = ''
              mkdir -p /nix/var/nix/profiles/per-user/grzegorz
            '';
            deps = [];
          };
        };
      };
    };
  };
}
