{
  config,
  lib,
  dream2nix,
  ...
}: let
  this-flake = import ../default.nix {inherit (config.deps.stdenv.buildPlatform) system;};
  inherit (this-flake) inputs;
  poetryLockRaw = lib.importTOML ../poetry.lock;
  ruffVersion =
    (
      lib.findFirst
      (p: p ? name && p.name == "ruff")
      (lib.throw "ruff not found inside poetry.lock")
      poetryLockRaw.package
    )
    .version;
in {
  imports = [
    dream2nix.modules.dream2nix.rust-cargo-lock
    dream2nix.modules.dream2nix.buildRustPackage
  ];

  deps = {nixpkgs, ...}: {
    inherit
      (nixpkgs)
      installShellFiles
      rust-jemalloc-sys
      stdenv
      ;
    CoreServices =
      if nixpkgs.stdenv.isDarwin
      then nixpkgs.darwin.apple_sdk.frameworks.CoreServices
      else null;
    # For phases
    ruff-nixpkgs = nixpkgs.ruff;
  };

  name = lib.mkForce "ruff";
  version = lib.mkForce ruffVersion;

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
