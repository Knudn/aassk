import os
import subprocess
import logging
import signal
import sys
import sqlite3
import requests

def Check_Event(event):
    from app.models import ActiveEvents
    from app import db as my_db
    event_query = ActiveEvents.query.filter(ActiveEvents.event_file.like(event[0]["db_file"][-15:].replace(".sqlite",""))).all()
    if len(event_query) == 0:
        return False
    else:
        return True

def Get_active_drivers(g_config, event_data_dict):
    with sqlite3.connect(g_config["project_dir"]+"site.db") as conn:
        cursor = conn.cursor()
        if event_data_dict["MODE"] == 3 or event_data_dict["MODE"] == 2:
            active_drivers_sql = cursor.execute("SELECT D1, D2 FROM active_drivers").fetchall()
            active_drivers = {"D1":active_drivers_sql[0][0],"D2":active_drivers_sql[0][1]}

    return active_drivers

def export_events():
    from app.models import ActiveEvents

    g_config = GetEnv()

    events = ActiveEvents.query.order_by(ActiveEvents.sort_order).all()
    for a in events:
        print(a)
    data = []
    for a in events:
        event= [{'db_file':g_config["db_location"]+str(a.event_file)+".sqlite", 'SPESIFIC_HEAT':a.run}]
        data.append(format_startlist(event,True))

    return data


def update_info_screen(id):
    from app import db
    from app.models import InfoScreenAssetAssociations, InfoScreenAssets, InfoScreenInitMessage
    id = 1
    assets = InfoScreenAssetAssociations.query.filter_by(infoscreen=id)
    infoscreen_url = InfoScreenInitMessage.query.filter_by(id=id).first()
    port = "8000"
    infoscreen_url = f'http://{infoscreen_url.ip}:{port}/update_index'
    json_data = []
    for a in assets:
        entry = {}
        asset_name = InfoScreenAssets.query.filter_by(id=a.asset).first()
        entry = {"name":asset_name.name, "url":asset_name.asset, "timer":a.timer}
        json_data.append(entry)
    
    requests.post(infoscreen_url, json=json_data)

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


def intel_sort():
    from app import db
    from app.models import ActiveEvents, EventOrder, EventType
    from sqlalchemy import or_
    from app.lib.db_func import map_database_files
    from app.lib.utils import GetEnv

    #Get data for event_type
    event_types_list = []
    event_types = EventType.query.all()
    for event_type in event_types:
        event_types_list.append(event_type)
    
    
    
    #Get data for event_order
    event_order_list = []
    event_types = EventOrder.query.all()
    for event_order in event_types:
        event_order_list.append(event_order)


    new_event_list = []
    new_type_dict = {}
    active_events = ActiveEvents.query.all()
    for g in event_order_list:
        for a in active_events:
            for b in event_types_list:
                if b.name not in new_type_dict:
                    new_type_dict[b.name] = []
                if str(b.name) in str(a.event_name) and g.name in a.event_name:
                    new_type_dict[b.name].append(a)

    count = 1

    for a in new_type_dict:
        
        for g in event_types_list:
            if g.finish_heat == True:
                finish_heat = True
            else:
                finish_heat = False

        for b in new_type_dict[a]:

            b.sort_order = count
            count += 1

        db.session.add_all(new_type_dict[a])
        db.session.commit()

    


    active_events = ActiveEvents.query.order_by(ActiveEvents.sort_order).all()
    new_type_dict = {}
    for event_type in event_types_list:
        filtered_events = [event for event in active_events if event_type.name in event.event_name]
        if event_type.finish_heat:
            # Sort by run first, then by sort_order within each run
            sorted_events = sorted(filtered_events, key=lambda x: (x.run, x.sort_order))
        else:
            # Sort just by sort_order
            sorted_events = sorted(filtered_events, key=lambda x: x.sort_order)
        
        new_type_dict[event_type.name] = sorted_events
                        
    count = 1
    for a in new_type_dict:

        for b in new_type_dict[a]:

            b.sort_order = count
            count += 1

        db.session.add_all(new_type_dict[a])
        db.session.commit()

def format_startlist(event,include_timedata=False):
    import json
    g_config = GetEnv()
    print(event)
    if Check_Event(event) == True:
        with sqlite3.connect(event[0]["db_file"]) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM startlist_r{0};".format(event[0]["SPESIFIC_HEAT"]))
            startlist_data = cursor.fetchall()
            event_data = cursor.execute("SELECT MODE, RUNS, TITLE1, TITLE2 FROM db_index;").fetchall()
            event_data_dict={"MODE":event_data[0][0],"HEATS":event_data[0][1], "HEAT":int(event[0]["SPESIFIC_HEAT"]),"TITLE_1":event_data[0][2], "TITLE_2":event_data[0][3]}

            cursor.execute("SELECT * FROM drivers")
            drivers_data = cursor.fetchall()
            

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
                        for a in time_data:
                            if str(a[0]) == str(driver_id):
                                driver_info["time_info"] = {"INTER_1":a[1], "INTER_2":a[2], "SPEED":a[3], "PENELTY":a[4], "FINISHTIME":a[5]}
                                if a[5] == 0 or a[4] != 0:
                                    driver_info["status"] = 0
                                    started = False

                        drivers_in_race.append(driver_info)


                        if len(drivers_in_race) == 2 and (event_data_dict["MODE"] == 3 or event_data_dict["MODE"] == 2):
                            if "status" in drivers_in_race[0] and drivers_in_race[1]["time_info"]["FINISHTIME"] > 0:
                                drivers_in_race[1]["status"] = 1
                                drivers_in_race[0]["status"] = 2
                                
                            elif "status" in drivers_in_race[1] and drivers_in_race[0]["time_info"]["FINISHTIME"] > 0:
                                drivers_in_race[0]["status"] = 1
                                drivers_in_race[1]["status"] = 2

                            if drivers_in_race[0]["time_info"]["FINISHTIME"] < drivers_in_race[1]["time_info"]["FINISHTIME"] and not "status" in drivers_in_race[0]:

                                drivers_in_race[0]["status"] = 1
                                drivers_in_race[1]["status"] = 2

                            elif drivers_in_race[0]["time_info"]["FINISHTIME"] > drivers_in_race[1]["time_info"]["FINISHTIME"] and not "status" in drivers_in_race[1]:
                                drivers_in_race[1]["status"] = 1
                                drivers_in_race[0]["status"] = 2

                race_info = {
                    "race_id": race_id,
                    "drivers": drivers_in_race,
                }
                
                structured_races.append(race_info)
        return structured_races
    else:
        logging.error(f"Active event not initiated operation")
        return "None"