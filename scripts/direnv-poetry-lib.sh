# shellcheck shell=bash

# Adapted from the layout_poetry() provided by the Direnv Wiki
# https://github.com/direnv/direnv/wiki/Python/#poetry

# Distributed under the MIT License
# Copyright (c) 2019 zimbatm and contributors
# Copyright (c) 2024 Yi-Ting Yu, Pin-Yen Lin, Yueh-Shun Li and the Transcript Timestamper community

layout_poetry() {
	# This project contains existing `pyproject.toml`.
	# There must be something wrong should the file be absent.
	if [[ ! -f "pyproject.toml" ]]; then
		log_status "No pyproject.toml found. Please execute \`poetry init\` to create a pyproject.toml first."
		exit 2
	fi

	if [[ -d ".venv" ]]; then
		VIRTUAL_ENV="$(pwd)/.venv"
	else
		VIRTUAL_ENV="$(poetry env info --path || true)"
	fi

	if [[ -z "$VIRTUAL_ENV" || ! -d "$VIRTUAL_ENV" ]]; then
		log_status "No virtual environment exists. Executing \`poetry install\` to create one."
		poetry install
		VIRTUAL_ENV="$(poetry env info --path)"
	fi

	PATH_add "$VIRTUAL_ENV/bin"
	export POETRY_ACTIVE=1 # or VENV_ACTIVE=1
	export VIRTUAL_ENV
}
