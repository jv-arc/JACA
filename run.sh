#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR=$(pwd)
VENV_PATH="$PROJECT_DIR/.linux_venv"


echo "Checking Python Virtual Environment"

if [[ ! -f "$VENV_PATH/bin/activate" ]]; then
    echo "Creating virtual environment: $VENV_PATH"
    python3 -m venv "$VENV_PATH"
fi

source "$VENV_PATH/bin/activate"


echo "Checking Libraries"
pip install -r requirements.txt


if [[ -f .env ]]
 then
    set -o allexport
    source .env
    set +o allexport
else
    echo "Error: .env file not found." >&2
    exit 1
fi


config_file="./app/data/app_config.json"
backup_file="${config_file}.bak"

cleanup() {
    if [[ -f "$backup_file"  ]]
     then
        mv "$backup_file" "$config_file"
    fi
}
trap cleanup EXIT

cp "$config_file" "$backup_file"

jq --arg key "$api_key" '.api_key = $key' "$backup_file" > "$config_file"


if [[ -f ./app/ui/Home.py ]]; then
    python -m streamlit run app/ui/Home.py
else
    echo "Error: Test entrypoint './app/ui/Home.py' not found." >&2
    exit 1
fi

