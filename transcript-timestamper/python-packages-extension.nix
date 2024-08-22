final: prev: let
  this-flake = import ../. {inherit (final.stdenv.hostPlatform) system;};
  inherit
    (this-flake.inputs)
    nixpkgs-dragonmapper
    ;
  callPackageFromNixpkgs = nixpkgs: subPath:
    final.callPackage "${nixpkgs}/${subPath}";
  callPythonModuleFromNixpkgs = nixpkgs: subPath:
    callPackageFromNixpkgs nixpkgs "pkgs/development/python-modules/${subPath}";
in {
  dragonmapper = callPythonModuleFromNixpkgs nixpkgs-dragonmapper "dragonmapper" {};

  # dragonmapper dependency
  hanzidentifier = callPythonModuleFromNixpkgs nixpkgs-dragonmapper "hanzidentifier" {};

  # ipython-8.24.0 not supported for interpreter python3.9
  python-dotenv = prev.python-dotenv.override (final.lib.optionalAttrs (final.pythonOlder "3.10") {
    ipython = null;
  });

  transcript-timestamper = final.callPackage ./package.nix {};

  # dragonmapper dependency
  zhon = callPythonModuleFromNixpkgs nixpkgs-dragonmapper "zhon" {};
}
