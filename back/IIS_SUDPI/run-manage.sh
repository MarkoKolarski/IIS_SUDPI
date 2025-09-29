#!/usr/bin/env bash
SCRIPT_DIR=$(dirname "$(realpath "$0")")
VENV_PATH="$SCRIPT_DIR/.venv"
source "$VENV_PATH/bin/activate"
python "$SCRIPT_DIR/manage.py" "$@"
deactivate
