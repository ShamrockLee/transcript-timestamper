{
  lib,
  # Build helpers
  buildPythonPackage,
  # Native build inputs
  poetry-core,
  pytestCheckHook,
  # Build inputs
  dragonmapper,
  numpy,
  pandas,
  whisper,
}: let
  pyprojectTOMLAttrs = lib.importTOML ./pyproject.toml;
  # TODO(@ShamrockLee):
  # Switch to pyprojectTomlAttrs.project
  # once python-poetry/poetry#9135 gets merged and released.
  pyprojectTOMLMetadata = pyprojectTOMLAttrs.tool.poetry;
in
  buildPythonPackage {
    pname = "transcript-timestamper";
    inherit (pyprojectTOMLMetadata) version;
    pyproject = true;

    src = with lib.fileset;
      toSource {
        root = ./.;
        # Get the filesets of files that are both
        # - In this directory
        # - Tracked by the Git repository (whose project root is the parent directory)
        fileset = intersection ./. (gitTracked ../.);
      };

    build-system = [poetry-core];

    dependencies = [
      dragonmapper
      numpy
      pandas
      whisper
    ];

    # There is currently no pytest tests.
    doCheck = false;

    nativeCheckInputs = [
      pytestCheckHook
    ];

    pythonImportsCheck = ["transcript_timestamper"];

    meta = {
      description = pyprojectTOMLMetadata.description;
      licenses = lib.getLicenseFromSpdxId pyprojectTOMLMetadata.license;
    };
  }
