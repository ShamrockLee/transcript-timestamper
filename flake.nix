{
  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixos-24.05";
  inputs.flake-parts.url = "github:hercules-ci/flake-parts";
  inputs.alejandra.url = "github:kamadorueda/alejandra/3.0.0";
  inputs.alejandra.inputs.nixpkgs.follows = "nixpkgs";
  inputs.devshell.url = "github:numtide/devshell";
  inputs.devshell.inputs.nixpkgs.follows = "nixpkgs";
  # Build ruff of custom version with dream2nix
  inputs.dream2nix.url = "github:nix-community/dream2nix";
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
      perSystem = {
        config,
        self',
        inputs',
        pkgs,
        system,
        ...
      }: let
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
      in {
        devshells.infra = {
          packages = with self'.packages; [
            alejandra
            ruff
            poetry
            shfmt
            treefmt
          ];
        };
        devShells.poetryenv-transcript-timestamper = poetry2nix.mkPoetryEnv {
          projectDir = ./transcript-timestamper;
          groups = ["dev"];
          checkGroups = ["test"];
        };
        devShells.poetryenv-transcript-timestamper-ui = poetry2nix.mkPoetryEnv {
          projectDir = ./transcript-timestamper-ui;
        };
        devShells.poetryenv-twly-meeting-fetchers = (poetry2nix.mkPoetryEnv {
          projectDir = ./twly-meeting-fetchers;
          groups = ["dev"];
        }).env.overrideAttrs (finalAttrs: previousAttrs: {
          buildInputs = previousAttrs.buildInputs or [] ++ (with pkgs; [
            ffmpeg-headless
          ]);
        });
        devShells.default = config.devShells.infra;
        packages = {
          inherit
            (pkgs)
            poetry
            shfmt
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
                CoreService =
                  if nixpkgs.stdenv.isDarwin
                  then nixpkgs.darwin.apple_sdk.frameworks.CoreService
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
                  CoreService
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
        };
      };
      systems = lib.attrNames inputs.nixpkgs.legacyPackages;
    };
}
