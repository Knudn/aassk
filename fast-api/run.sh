#!/bin/bash

function check_script_execution() {
    if ! command -v python3 &> /dev/null || ! command -v pip3 &> /dev/null || ! pip3 list | grep -q virtualenv; then
        echo "Script has not been executed: Python3, pip3, or virtualenv is missing."
        return 1
    fi

    if [ ! -d "fastapi_app_env" ]; then
        echo "Script has not been executed: Virtual environment 'fastapi_app_env' does not exist."
        return 1
    fi

    source ./fastapi_app_env/bin/activate
    if ! pip list | grep -q fastapi || ! pip list | grep -q uvicorn || ! pip list | grep -q sqlalchemy; then
        echo "Script has not been executed: FastAPI, Uvicorn, or SQLAlchemy is not installed in the virtual environment."
        deactivate
        return 1
    fi
    deactivate

    echo "Script has been executed previously."
    return 0
}

check_script_execution

if [ $? -eq 1 ]; then
    ./install.sh
fi

./vnc/vnc_config.sh