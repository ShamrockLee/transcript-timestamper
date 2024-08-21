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

  transcript-timestamper = final.callPackage ./package.nix {};

  # dragonmapper dependency
  zhon = callPythonModuleFromNixpkgs nixpkgs-dragonmapper "zhon" {};
}
