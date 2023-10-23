import os
import subprocess
import logging
import signal
import sys
import sqlite3

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

def format_startlist(event,include_timedata=False):
    import json

    with sqlite3.connect(event[0]["db_file"]) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM startlist_r{0};".format(event[0]["SPESIFIC_HEAT"]))
        startlist_data = cursor.fetchall()
        cursor.execute("SELECT * FROM drivers")
        drivers_data = cursor.fetchall()
        if include_timedata:
            cursor.execute("SELECT CID, INTER_1, INTER_2, SPEED, PENELTY, FINISHTIME FROM driver_stats_r{0};".format(event[0]["SPESIFIC_HEAT"]))
            time_data = cursor.fetchall()

        drivers_dict = {driver[0]: driver[1:] for driver in drivers_data}
        structured_races = []

        for race in startlist_data:
            race_id = race[0]
            drivers_in_race = []

            for driver_id in race[1:]:
                driver_data = drivers_dict.get(driver_id)
                if driver_data:
                    driver_info = {
                        "id": driver_id,
                        "first_name": driver_data[0],
                        "last_name": driver_data[1],
                        "club": driver_data[2],
                        "vehicle": driver_data[3]
                    }
                    if include_timedata:
                        for a in time_data:
                            if str(a[0]) == str(driver_id):
                                driver_info["time_info"] = {"INTER_1":a[1], "INTER_2":a[2], "SPEED":a[3], "PENELTY":a[4], "FINISHTIME":a[5]}
                    drivers_in_race.append(driver_info)

            race_info = {
                "race_id": race_id,
                "drivers": drivers_in_race
            }
            structured_races.append(race_info)

        

    return structured_races

