#!/usr/bin/env python3

import argparse
import filecmp
from pathlib import Path
import shutil
import sys

build_systems: str = [
    "poetry",
]
template_name_dict: dict[str, str] = {
    build_system: "envrc_{}.in".format(build_system) for build_system in build_systems
}

parser = argparse.ArgumentParser(
    description="Choose the direnv .envrc template, or delete the .envrc files."
)
parser.add_argument(
    "build_system", choices=["clean"] + build_systems, help="The choosen build system. \"clean\" to delete \".envrc\"."
)
parser.add_argument(
    "-k", "--keep-going", action="store_true", help="Overwrite existing .envrc files."
)
parser.add_argument(
    "-n",
    "--dry-run",
    action="store_true",
    help="Perform a trial run with no changes made.",
)
parser.add_argument("-v", "--verbose", action="count", help="Increase verbosity.")

args = parser.parse_args()

dry_run: bool = args.dry_run
verbosity: int = args.verbose

to_clean: bool = args.build_system == "clean"
template_name: str = ""

if args.build_system == "poetry":
    template_name = "envrc_poetry.in"

path0 = Path(sys.argv[0])

if path0.parent.name != "scripts":
    print(
        "choose-envrc.py cannot locate the project root. Please execute with a path containing `scripts/choose-envrc.py`.",
        file=sys.stderr,
    )
    exit(1)

# The project root
path_root = path0.parent.parent

dirs = [
    path_root,
    path_root / "transcript-timestamper",
    path_root / "transcript-timestamper-ui",
    path_root / "twly-meeting-fetchers",
]

dirs_status: list[str] = [0] * len(dirs)

for d in dirs:
    path_envrc = d / ".envrc"
    if to_clean:
        if dry_run or verbosity:
            print("Unlinking {}".format(path_envrc))
        if not dry_run:
            path_envrc.unlink(missing_ok=True)
        continue
    path_template = d / template_name
    if path_envrc.exists() and filecmp.cmp(path_template, path_envrc):
        if verbosity:
            print("{} and {} are the same.".format(path_template, path_envrc))
        continue
    if verbosity:
        print("{} and {} are the different.".format(path_template, path_envrc))
    if dry_run or verbosity:
        print("Copying {} to {}.".format(path_template, path_envrc), file=sys.stderr)
    if not dry_run:
        shutil.copyfile(path_template, path_envrc)
