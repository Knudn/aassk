import os
import subprocess
import logging
import signal
import sys

def GetEnv():
    from app.models import GlobalConfig

    global_config = GlobalConfig.query.all()
    
    if not global_config:
        return {}

    first_row = global_config[0]
    row_dict = {key: value for key, value in first_row.__dict__.items() if not key.startswith('_')}

    return row_dict

def manage_process(python_program_path: str, operation: str) -> None:
    from app.models import GlobalConfig

    global_config = GlobalConfig.query.get(1)
    python_program_path = global_config.project_dir+python_program_path
    python_executable = sys.executable
    pid_file_path = f"{python_program_path}.pid"

    if operation == 'start':
        if os.path.exists(pid_file_path):
            logging.error(f"PID file {pid_file_path} already exists. Process may already be running.")
            return
        
        with open(pid_file_path, 'w') as pid_file:
            process = subprocess.Popen([python_executable, python_program_path], preexec_fn=os.setpgrp)
            pid_file.write(str(process.pid))
            
        logging.info(f"Process started with PID {process.pid}")
        
    elif operation == 'stop':
        if not os.path.exists(pid_file_path):
            logging.error(f"PID file {pid_file_path} does not exist. Process may not be running.")
            return
        
        with open(pid_file_path, 'r') as pid_file:
            pid = int(pid_file.read())
            os.killpg(pid, signal.SIGTERM)
            os.remove(pid_file_path)
        
        logging.info(f"Process with PID {pid} stopped")
        
    elif operation == 'restart':
        if os.path.exists(pid_file_path):
            manage_process(python_program_path, 'stop')
        manage_process(python_program_path, 'start')
        
    else:
        logging.error(f"Unsupported operation: {operation}")

