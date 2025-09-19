#!/usr/bin/env bash
set -euo pipefail

if [[ -f ./.venv/bin/activate ]]; then
  source ./.venv/bin/activate
else
  echo "Error: Virtualenv not found at ./.venv/bin/activate" >&2
  exit 1
fi

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

jq --arg key "$apikey" '.apikey = $key' "$backup_file" > "$config_file"


if [[ -f ./app/ui/Home.py ]]; then
    python -m streamlit run app/ui/Home.py
else
    echo "Error: Test entrypoint './app/ui/Home.py' not found." >&2
    exit 1
fi

