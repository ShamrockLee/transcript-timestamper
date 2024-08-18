final: prev: let
  this-flake = import ../. { inherit (final.stdenv.hostPlatform) system; };
  inherit
    (this-flake.inputs)
    nixpkgs-pym3u8downloader
    ;
  callPackageFromNixpkgs = nixpkgs: subPath:
    final.callPackage "${nixpkgs}/${subPath}";
  callPythonModuleFromNixpkgs = nixpkgs: subPath:
    callPackageFromNixpkgs nixpkgs "pkgs/development/python-modules/${subPath}";
in {
  # pym3u8downloader dependency
  pycolorecho = callPythonModuleFromNixpkgs nixpkgs-pym3u8downloader "pycolorecho" {};

  # pym3u8downloader dependency
  pyloggermanager = callPythonModuleFromNixpkgs nixpkgs-pym3u8downloader "pyloggermanager" {};

  pym3u8downloader = callPythonModuleFromNixpkgs nixpkgs-pym3u8downloader "pym3u8downloader" {};
}
