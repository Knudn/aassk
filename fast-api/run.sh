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
    
    echo "Script has been executed previously."
    return 0
}

check_script_execution

source ./fastapi_app_env/bin/activate

if [ $? -eq 1 ]; then
    ./install.sh
fi

./vnc/vnc_config.sh