#!/usr/bin/env bash

echo "Performing environment setup..."
ORIGINAL_DIRECTORY="`pwd`"
LOCAL_DIRECTORY="`dirname ${0}`"
cd ${LOCAL_DIRECTORY}
VENV_DIR=venv
if [[ ! -d "$VENV_DIR" ]]; then
    echo "$VENV_DIR directory not detected. Creating virtual environment..."
    python3 -m venv ${VENV_DIR}
fi
