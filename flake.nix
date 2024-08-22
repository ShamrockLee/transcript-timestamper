{
  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixos-24.05";
  inputs.flake-compat.url = "github:nix-community/flake-compat";
  inputs.flake-parts.url = "github:hercules-ci/flake-parts";
  inputs.alejandra.url = "github:kamadorueda/alejandra/3.0.0";
  inputs.alejandra.inputs.nixpkgs.follows = "nixpkgs";
  inputs.devshell.url = "github:numtide/devshell";
  inputs.devshell.inputs.nixpkgs.follows = "nixpkgs";
  # Build ruff of custom version with dream2nix
  inputs.dream2nix.url = "github:nix-community/dream2nix";
  # The branch name contains an unfortunate typo.
  inputs.nixpkgs-dragonmapper.url = "github:ShamrockLee/nixpkgs/dragonmappr";
  inputs.nixpkgs-pym3u8downloader.url = "github:ShamrockLee/nixpkgs/pym3u8downloader";
  inputs.nixpkgs-unstable.url = "github:NixOS/nixpkgs/nixos-unstable";
  inputs.poetry2nix.url = "github:nix-community/poetry2nix";
  inputs.poetry2nix.inputs.nixpkgs.follows = "nixpkgs";
  inputs.ruff-source.url = "github:astral-sh/ruff/0.5.5";
  inputs.ruff-source.flake = false;

  outputs = {self, ...} @ inputs: let
    inherit (inputs.nixpkgs) lib;
  in
    inputs.flake-parts.lib.mkFlake {inherit inputs;} {
      imports = [
        inputs.devshell.flakeModule
      ];
      flake = {
        pythonPackageExtensions = {
          transcript-timestamper = import ./transcript-timestamper/python-packages-extension.nix;
          transcript-timestamper-ui = import ./transcript-timestamper-ui/python-packages-extension.nix;
          twly-meeting-fetchers = import ./twly-meeting-fetchers/python-packages-extension.nix;
        };
      };
      perSystem = {
        config,
        self',
        inputs',
        pkgs,
        system,
        ...
      }: let
        pkgsUnstable = inputs'.nixpkgs-unstable.legacyPackages;
        poetry2nix = inputs.poetry2nix.lib.mkPoetry2Nix {inherit pkgs;};
        callDream2NixModule = module:
          inputs.dream2nix.lib.evalModules {
            packageSets.nixpkgs = pkgs;
            modules = [
              module
              {
                paths.projectRoot = ./.;
                paths.projectRootFile = ./flake.nix;
                paths.package = ./.;
              }
            ];
          };
        pythons = {
          inherit
            (pkgs)
            python3
            python39
            python310
            python311
            python312
            ;
        };
        # Python packages with all its modules in the Nixpkgs binary cache
        binaryCachedPythons =
          lib.filterAttrs (
            pythonName: python:
              pkgs."${pythonName}Packages".recurseForDerivations or false
          )
          pythons;
      in {
        checks =
          lib.concatMapAttrs (pythonName: python: {
            "transcript-timestamper_${pythonName}" = self'.packages."${pythonName}-overridden-transcript-timestamper".pkgs.transcript-timestamper;
            "transcript-timestamper-ui_${pythonName}" = self'.packages."${pythonName}-overridden-transcript-timestamper-ui".pkgs.transcript-timestamper-ui;
          })
          binaryCachedPythons;
        devshells =
          {
            infra = {
              env = [
                {
                  # pip defaults to timeout after 15 seconds.
                  # Set to a longer period to download large packages smoothly.
                  name = "POETRY_REQUESTS_TIMEOUT";
                  value = 300;
                }
              ];
              packages = with self'.packages; [
                act
                alejandra
                ruff
                poetry
                shellcheck
                shfmt
                treefmt
              ];
            };
          }
          // lib.concatMapAttrs (pythonName: python: {
            "pythondev-twly-meeting-fetchers_${pythonName}" = {
              packages =
                [
                  (self'.packages."${pythonName}-overridden-transcript-timestamper-ui".withPackages (ps: (with ps; [
                    pandas
                    pypdf
                    py-pdf-parser
                    selenium
                  ])))
                ]
                ++ (with pkgs; [
                  ffmpeg-headless
                ]);
            };
          })
          pythons;
        devShells =
          {
            default = config.devShells.infra;
          }
          // lib.genAttrs [
            "poetryenv-transcript-timestamper"
            "poetryenv-transcript-timestamper-ui"
            "poetryenv-twly-meeting-fetchers"
            "pythondev-transcript-timestamper"
            "pythondev-transcript-timestamper-ui"
            "pythondev-twly-meeting-fetchers"
          ] (name: self'.devShells."${name}_python3")
          // lib.concatMapAttrs (pythonName: python: {
            "poetryenv-transcript-timestamper_${pythonName}" = poetry2nix.mkPoetryEnv {
              projectDir = ./transcript-timestamper;
              groups = ["dev"];
              checkGroups = ["test"];
              inherit python;
            };
            # PySide6 currently doesn't build through poetry2nix.
            # Use `pythondev-transcript-timestamper-ui` instead.
            "poetryenv-transcript-timestamper-ui_${pythonName}" = poetry2nix.mkPoetryEnv {
              projectDir = ./transcript-timestamper-ui;
              inherit python;
            };
            "poetryenv-twly-meeting-fetchers_${pythonName}" =
              (poetry2nix.mkPoetryEnv {
                projectDir = ./twly-meeting-fetchers;
                groups = ["dev"];
                inherit python;
              })
              .env
              .overrideAttrs (finalAttrs: previousAttrs: {
                buildInputs =
                  previousAttrs.buildInputs
                  or []
                  ++ (with pkgs; [
                    ffmpeg-headless
                  ]);
              });
            "pythondev-transcript-timestamper_${pythonName}" =
              self'.packages."${pythonName}-overridden-transcript-timestamper".pkgs.transcript-timestamper;
            "pythondev-transcript-timestamper-ui_${pythonName}" =
              self'.packages."${pythonName}-overridden-transcript-timestamper-ui".pkgs.transcript-timestamper-ui;
          })
          pythons;
        packages =
          {
            inherit
              (pkgs)
              act
              poetry
              shellcheck
              shfmt
              ;
            inherit
              (pkgsUnstable)
              treefmt
              ;
            alejandra =
              inputs'.alejandra.packages.default
              or (import inputs.nixpkgs {
                overlays = [inputs.alejandra.overlay];
                inherit system;
              })
              .alejandra;
            ruff = callDream2NixModule (
              {
                config,
                lib,
                dream2nix,
                ...
              }: {
                imports = [
                  dream2nix.modules.dream2nix.rust-cargo-lock
                  dream2nix.modules.dream2nix.buildRustPackage
                ];

                deps = {nixpkgs, ...}: {
                  inherit
                    (nixpkgs)
                    installShellFiles
                    rust-jemalloc-sys
                    ;
                  CoreServices =
                    if nixpkgs.stdenv.isDarwin
                    then nixpkgs.darwin.apple_sdk.frameworks.CoreServices
                    else null;
                  # For phases
                  ruff-nixpkgs = nixpkgs.ruff;
                };

                name = lib.mkForce "ruff";
                version = lib.mkForce "0.5.5";

                mkDerivation = {
                  src = inputs.ruff-source.outPath;
                  nativeBuildInputs = with config.deps; [
                    installShellFiles
                  ];
                  buildInputs = with config.deps; [
                    rust-jemalloc-sys
                    CoreServices
                  ];
                  inherit
                    (config.deps.ruff-nixpkgs)
                    postInstall
                    ;
                };

                public = {
                  meta = {
                    inherit
                      (config.deps.ruff-nixpkgs.meta)
                      description
                      mainProgram
                      ;
                  };
                };
              }
            );
          }
          // lib.mapAttrs' (pythonName: python: {
            name = "${pythonName}-overridden-transcript-timestamper";
            value = python.override {
              packageOverrides = self.pythonPackageExtensions.transcript-timestamper;
            };
          })
          pythons
          // lib.mapAttrs' (pythonName: python: {
            name = "${pythonName}-overridden-transcript-timestamper-ui";
            value = python.override {
              packageOverrides = lib.composeManyExtensions [
                self.pythonPackageExtensions.transcript-timestamper
                self.pythonPackageExtensions.transcript-timestamper-ui
              ];
            };
          })
          pythons
          // lib.mapAttrs' (pythonName: python: {
            name = "${pythonName}-overridden-twly-meeting-fetchers";
            value = python.override {
              packageOverrides = self.pythonPackageExtensions.twly-meeting-fetchers;
            };
          })
          pythons;
      };
      systems = lib.attrNames inputs.nixpkgs.legacyPackages;
    };
}
