import os
import subprocess
import logging
import signal
import sys
import sqlite3

def Check_Event(event):
    from app.models import ActiveEvents
    from app import db as my_db

    event_query = ActiveEvents.query.filter(ActiveEvents.event_file.like(event[0]["db_file"][-15:].replace(".sqlite",""))).all()
    print(event_query)
    if len(event_query) == 0:
        return False
    else:
        return True

def Get_active_drivers(g_config, event_data_dict):
    with sqlite3.connect(g_config["project_dir"]+"site.db") as conn:
        cursor = conn.cursor()
        print(event_data_dict["MODE"])
        if event_data_dict["MODE"] == 3 or event_data_dict["MODE"] == 2:
            active_drivers_sql = cursor.execute("SELECT D1, D2 FROM active_drivers").fetchall()
            active_drivers = {"D1":active_drivers_sql[0][0],"D2":active_drivers_sql[0][1]}

    return active_drivers


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
    g_config = GetEnv()

    

    if Check_Event(event) == True:
        with sqlite3.connect(event[0]["db_file"]) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM startlist_r{0};".format(event[0]["SPESIFIC_HEAT"]))
            startlist_data = cursor.fetchall()
            event_data = cursor.execute("SELECT MODE, RUNS, TITLE1, TITLE2 FROM db_index;").fetchall()
            event_data_dict={"MODE":event_data[0][0],"HEATS":event_data[0][1], "HEAT":int(event[0]["SPESIFIC_HEAT"]),"TITLE_1":event_data[0][2], "TITLE_2":event_data[0][3]}

            cursor.execute("SELECT * FROM drivers")
            drivers_data = cursor.fetchall()
            
            if include_timedata:
                cursor.execute("SELECT CID, INTER_1, INTER_2, SPEED, PENELTY, FINISHTIME FROM driver_stats_r{0};".format(event[0]["SPESIFIC_HEAT"]))
                time_data = cursor.fetchall()

            drivers_dict = {driver[0]: driver[1:] for driver in drivers_data}
            structured_races = []
            structured_races.append({"race_config":event_data_dict})

            if event_data_dict["MODE"] == 3 or event_data_dict["MODE"] == 2:
                active_drivers = Get_active_drivers(g_config, event_data_dict)
                driver_entries = []
                count = 0
                for b in range(0,int(len(startlist_data)/2)):
                    driver_entries.append((b+1, startlist_data[count][1],startlist_data[count+1][1]))
                    count = count+2   
            else:
                driver_entries = []
                count = 0

                for b in range(0,int(len(startlist_data))):
                    driver_entries.append((b+1, startlist_data[count][1]))
                    count = count + 1
                active_drivers = {"D1":"None"}
                

            for race in driver_entries:
                race_id = race[0]
                drivers_in_race = []
                for driver_id in race[1:]:

                    driver_data = drivers_dict.get(driver_id)
                    if driver_data:
                        if int(driver_id) in active_drivers.values():
                            active = True
                        else:
                            active = False
                        
                        
                        driver_info = {
                            "id": driver_id,
                            "first_name": driver_data[0],
                            "last_name": driver_data[1],
                            "club": driver_data[2],
                            "vehicle": driver_data[3],
                            "active": active
                        }
                        if include_timedata:
                            for a in time_data:
                                if str(a[0]) == str(driver_id):
                                    driver_info["time_info"] = {"INTER_1":a[1], "INTER_2":a[2], "SPEED":a[3], "PENELTY":a[4], "FINISHTIME":a[5]}
                                    if any(value is not None for value in driver_info["time_info"].values()):
                                        print("asd")
                                    else:
                                        print("ddddd")
                        drivers_in_race.append(driver_info)

                race_info = {
                    "race_id": race_id,
                    "drivers": drivers_in_race,
                }
                
                structured_races.append(race_info)
        return structured_races
    else:
        logging.error(f"Active event not initiated operation")
        return "None"