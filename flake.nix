{
  description = "A REST API for managing a MPV instance over via a RPC socket";

  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";

  outputs = {
    self,
    nixpkgs,
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
        version = "23.6.0";
        src = fetchPypi {
          inherit pname version;
          hash = "sha256-gd0Ta2t7ef2otP7CRE2YIjlFVXecKYqJFVxnKHoYSQI=";
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
        propagatedBuildInputs = [ setuptools sanic sanic-ext youtube-dl mpv ];
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

    });

    apps = forAllSystems ({ system, pkgs, ...}: {
      default.type = "app";
      default.program = "${self.packages.${system}.grzegorz-run}/bin/grzegorz-run";
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
        systemd.services.grzegorz = lib.mkIf cfg.enable {
          description = "grzegorz";
          wantedBy = [ "default.target" ];
          serviceConfig = {
            User = "grzegorz";
            Group = "grzegorz";
            DynamicUser = true;
            #StateDirectory = "grzegorz";
            #CacheDirectory = "grzegorz";
            ExecStart = lib.escapeShellArgs [
              "${pkgs.cage}/bin/cage"
              "--"
              "${cfg.package}/bin/grzegorz-run"
              "--host" cfg.listenAddr
              "--port" cfg.listenPort
            ];
            Restart = "on-failure";
          };
        };

      };
    };


  };
}
