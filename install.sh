#!/usr/bin/env bash

APP_DIR=/opt/scan_monitor
BIN_DIR=${APP_DIR}/venv/bin
REPO_URI=https://github.com/agroome/scan_monitor.git

echo "PYTHONENV: ${BIN_DIR}"

if [[ -d "${APP_DIR}" ]]; then
    echo "${APP_DIR} already exists. Delete ${APP_DIR} and try again."
    exit 1
fi

git clone ${REPO_URI} ${APP_DIR}

# create virtual env
apt-get install -y python-venv
python3 -m venv ${APP_DIR}/venv

echo ${BIN_DIR}/pip

${BIN_DIR}/pip install -r ${APP_DIR}/requirements.txt
