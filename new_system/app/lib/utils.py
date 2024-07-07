import subprocess
import logging
import signal
import sys
import sqlite3
import requests
import psutil
import os
import select
from threading import Thread
from flask import current_app


def object_to_dict(obj):
    return {attr: getattr(obj, attr) for attr in dir(obj) if not attr.startswith('_') and not callable(getattr(obj, attr))}

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
        else:
            active_drivers_sql = cursor.execute("SELECT D1 FROM active_drivers").fetchall()
            active_drivers = {"D1":active_drivers_sql[0][0]}

    return active_drivers




def export_events():
    from app.models import ActiveEvents

    g_config = GetEnv()

    events = ActiveEvents.query.order_by(ActiveEvents.sort_order).all()

    data = []
    for a in events:
        event= [{'db_file':g_config["db_location"]+str(a.event_file)+".sqlite", 'SPESIFIC_HEAT':a.run}]
        data.append(format_startlist(event,True))

    return data

def convert_microseconds_to_time(microseconds):
    # convert microseconds to seconds
    seconds = microseconds / 1_000_000

    # calculate each unit and the remainder
    hours, rem = divmod(seconds, 3600)
    minutes, rem = divmod(rem, 60)
    seconds, rem = divmod(rem, 1)
    milliseconds = rem * 1000

    # return a string in the format "hours:minutes:seconds.milliseconds"
    return "{:02d}:{:02d}:{:02d}.{:03d}".format(int(hours), int(minutes), int(seconds), int(milliseconds))


def update_info_screen(id):
    from app import db
    from app.models import InfoScreenAssetAssociations, InfoScreenAssets, InfoScreenInitMessage
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
    if row_dict["use_intermediate"] == True:
        row_dict["event_dir"] = row_dict["intermediate_path"]

    return row_dict

def is_screen_session_running(session_name: str) -> bool:
    """Check if a Screen session with the given name is running."""
    try:
        # Command to list all Screen sessions
        list_sessions_cmd = "screen -ls"
        # Execute the command and decode the output
        sessions_output = subprocess.check_output(list_sessions_cmd, shell=True).decode()
        # Check if the session name is in the output
        return session_name in sessions_output
    except subprocess.CalledProcessError:
        # If the screen command fails, assume the session is not running
        return False

def manage_process_screen(python_program_path: str, operation: str, new_argument: str = None) -> None:
    from app.models import GlobalConfig
    import time, subprocess, shlex, logging

    global_config = GlobalConfig.query.get(1)
    program_file = python_program_path
    python_program_path = global_config.project_dir + "scripts/" + python_program_path
    python_executable = sys.executable
    program_name = os.path.basename(python_program_path)
    screen_session_name = f"session_{program_name}"

    def is_screen_session_running(session_name: str) -> bool:
        """Check if a Screen session with the given name is running."""
        try:
            list_sessions_cmd = "screen -ls"
            sessions_output = subprocess.check_output(list_sessions_cmd, shell=True).decode()
            return session_name in sessions_output
        except subprocess.CalledProcessError:
            return False

    if operation == 'start':

        if is_screen_session_running(screen_session_name):
            logging.error(f"Screen session {screen_session_name} may already be running.")
            return
        start_cmd = f"screen -dmS {screen_session_name} {python_executable} {shlex.quote(python_program_path)}"
        subprocess.Popen(start_cmd, shell=True)
        logging.info(f"Screen session {screen_session_name} started with program {program_name}")

    elif operation == 'stop':
        if not is_screen_session_running(screen_session_name):
            logging.error(f"Screen session {screen_session_name} may not be running.")
            return

        stop_cmd = f"screen -S {screen_session_name} -X quit"
        subprocess.Popen(stop_cmd, shell=True)
        logging.info(f"Screen session {screen_session_name} stopped")

    elif operation == 'restart':
        if is_screen_session_running(screen_session_name):
            manage_process_screen(python_program_path, 'stop')
            time.sleep(1)  # Wait a bit for the session to be fully stopped
        manage_process_screen(python_program_path, 'start')

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

def get_event_data_all(event):
    import json

    g_config = GetEnv()
    with sqlite3.connect(event[0]["db_file"]) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM drivers;".format(event[0]["db_file"]))
        drivers = cursor.fetchall()

        data = {}

        for a in event[0]["SPESIFIC_HEAT"]:
            
            cursor.execute("SELECT * FROM driver_stats_r{0};".format(a))
            driver_stats = cursor.fetchall()
            
            cursor.execute("SELECT * FROM startlist_r{0};".format(a))
            driver_startlist = cursor.fetchall()
            
            for start_entry in driver_startlist:
                for row in driver_stats:

                    driver = next((d for d in drivers if d[0] == row[0]), None)
                    if driver:
                        if driver[2] == "FILLER" or driver[1] == "FILLER":
                            
                            newdata = list(driver)
                            newdata[3] = "FILLER"
                            newdata[4] = "FILLER"
                            driver = tuple(newdata)

                        if a not in data:
                            data[a] = []
                        
                        if row[0] == start_entry[1]:
                            if (driver[:5] + row[4:7]) not in data[a]:
                                data[a].append(driver[:5] + row[4:7])

    return data

def get_active_events_sorted():

    from app.models import ActiveEvents
    from app.lib.db_operation import get_active_event
    event_order = ActiveEvents.query.order_by(ActiveEvents.sort_order).all()
    current_active_event = get_active_event()[0]

    data = []
    
    for a in event_order:

        if str(a.event_file) == str(current_active_event["db_file"]) and str(current_active_event["SPESIFIC_HEAT"]) == str(a.run):
            state = True
        else:
            state = False
        data.append({"Order":a.sort_order, "Event":a.event_name, "Enabled":a.enabled, "Heat":a.run, "Active":state, "Mode":a.mode})
        
    return data

def format_startlist(event, include_timedata=False):
    from app import db
    from app.models import EventData

    g_config = GetEnv()
    if Check_Event(event):
        event_file = event[0]["db_file"]
        specific_heat = int(event[0]["SPESIFIC_HEAT"])

        # Query the database using SQLAlchemy
        event_data = db.session.query(EventData).filter_by(DB_FILE=event_file, HEAT=specific_heat).all()
        if not event_data:
            return "None"

        # Get event configuration
        event_config = event_data[0]
        event_data_dict = {
            "MODE": event_config.MODE,
            "HEATS": event_config.RUNS,
            "HEAT": specific_heat,
            "TITLE_1": event_config.TITLE1,
            "TITLE_2": event_config.TITLE2,
            "DATE": event_config.DATE.strftime("%Y-%m-%d"),
            "CROSS": g_config["cross"]
        }

        structured_races = [{"race_config": event_data_dict}]

        # Get active drivers
        active_drivers = Get_active_drivers(g_config, event_data_dict)

        # Organize drivers into pairs or individual entries
        if event_data_dict["MODE"] in [2, 3]:
            driver_entries = [(i//2 + 1, d1.CID, d2.CID) for i, (d1, d2) in enumerate(zip(event_data[::2], event_data[1::2]))]
        else:
            driver_entries = [(i+1, d.CID) for i, d in enumerate(event_data)]

        for race in driver_entries:
            race_id = race[0]
            drivers_in_race = []

            for driver_id in race[1:]:
                driver_data = next((d for d in event_data if d.CID == driver_id), None)
                if driver_data:
                    active = driver_id in active_drivers.values()

                    driver_info = {
                        "id": driver_id,
                        "first_name": driver_data.FIRST_NAME,
                        "last_name": driver_data.LAST_NAME,
                        "club": driver_data.CLUB,
                        "vehicle": driver_data.SNOWMOBILE,
                        "active": active,
                        "time_info": {
                            "INTER_1": driver_data.INTER_1,
                            "INTER_2": driver_data.INTER_2,
                            "SPEED": driver_data.SPEED,
                            "PENELTY": driver_data.PENALTY,
                            "FINISHTIME": driver_data.FINISHTIME
                        }
                    }

                    if driver_data.FINISHTIME == 0 or driver_data.PENALTY != 0:
                        driver_info["status"] = 0

                    drivers_in_race.append(driver_info)

            # Handle status for drag race modes (2 and 3)
            if event_data_dict["MODE"] in [2, 3] and len(drivers_in_race) == 2:
                if drivers_in_race[0]["time_info"]["PENELTY"] > 0:
                    drivers_in_race[1]["status"] = 1
                    drivers_in_race[0]["status"] = 2
                elif drivers_in_race[1]["time_info"]["PENELTY"] > 0:
                    drivers_in_race[0]["status"] = 1
                    drivers_in_race[1]["status"] = 2
                elif "status" not in drivers_in_race[0] and drivers_in_race[1]["time_info"]["FINISHTIME"] and drivers_in_race[1]["time_info"]["PENELTY"] == 0:
                    drivers_in_race[1]["status"] = 1
                    drivers_in_race[0]["status"] = 2
                elif "status" not in drivers_in_race[1] and drivers_in_race[0]["time_info"]["FINISHTIME"] and drivers_in_race[0]["time_info"]["PENELTY"] == 0:
                    drivers_in_race[0]["status"] = 1
                    drivers_in_race[1]["status"] = 2
                elif drivers_in_race[0]["time_info"]["FINISHTIME"] < drivers_in_race[1]["time_info"]["FINISHTIME"] and "status" not in drivers_in_race[0]:
                    drivers_in_race[0]["status"] = 1
                    drivers_in_race[1]["status"] = 2
                elif drivers_in_race[0]["time_info"]["FINISHTIME"] > drivers_in_race[1]["time_info"]["FINISHTIME"] and "status" not in drivers_in_race[1]:
                    drivers_in_race[1]["status"] = 1
                    drivers_in_race[0]["status"] = 2

            elif event_data_dict["MODE"] == 0:
                race_id = specific_heat

            race_info = {
                "race_id": race_id,
                "drivers": drivers_in_race,
            }
            
            structured_races.append(race_info)

        return structured_races
    else:
        logging.error(f"Active event not initiated operation")
        return "None"


def reorder_list_based_on_dict(original_list, correct_order_dict):
    new_list = []
    temp_dict = {}

    for name, score in original_list:
        if score in temp_dict:
            temp_dict[score].append(name)
        else:
            temp_dict[score] = [name]

    for item in original_list:
        name, score = item
        # Check if this score needs reordering and if the name is in the correct order list
        if score in correct_order_dict and name in correct_order_dict[score]:
            # If the name is the next one to be placed according to the dictionary, add it to the new list
            if name == correct_order_dict[score][0]:
                new_list.append(item)
                correct_order_dict[score].pop(0)  # Remove the added name from the dictionary list
        else:
            # For scores not needing reordering or already handled, add them directly
            if name in temp_dict[score]:
                new_list.append(item)
                temp_dict[score].remove(name)  # Remove the added name from the temp_dict list

    return new_list

def get_active_driver_name(db, db_file, cid):
    from sqlalchemy import and_
    from app.models import EventData

    driver = db.session.query(EventData.FIRST_NAME, EventData.LAST_NAME).filter(
        and_(
            EventData.DB_FILE == db_file,
            EventData.CID == cid
        )
    ).first()
    
    return driver if driver else (None, None)

def fifo_monitor(app, fifo_path='/tmp/file_monitor_fifo', callback=None, g_config=None):
    import json
    if g_config.use_intermediate == True:
        g_config.event_dir = g_config.intermediate_path

    if not os.path.exists(fifo_path):
        os.mkfifo(fifo_path)

    def monitor_fifo():
        from app.lib.db_operation import full_db_reload
        import sqlite3
        import json
        import re
        import time

        fifo = os.open(fifo_path, os.O_RDONLY | os.O_NONBLOCK)
        poll = select.poll()
        poll.register(fifo, select.POLLIN)
        
        DB_PATH = "/mnt/intermediate/Online.scdb"
        with sqlite3.connect(DB_PATH) as con:
            cur = con.cursor()
            active_event = cur.execute("SELECT C_PARAM WHERE WHERE ;").fetchone()[0]
            
        while True:
            if poll.poll(1000):
                try:
                    
                    data = os.read(fifo, 4096).decode().strip()

                    if str(data) == "Online.scdb":
                        print("Online DB")
                        with sqlite3.connect(DB_PATH) as con:
                            cur = con.cursor()
                            time.sleep(2)
                            active_event = cur.execute("SELECT EVENT FROM active_drivers;").fetchone()[0]
                    else:
                        event_change = re.findall(r'\d+', data)
                        try:
                            if len(event_change) == 0:
                                print("FAIL", data)

                            else:
                                #full_db_reload(add_intel_sort=False, Event=file)
                                print("NOT ACTIVE", event_change)
                        except:
                            print("Error")

                    if data and callback:
                        with app.app_context():
                            callback(data)
                except OSError:
                    pass

    thread = Thread(target=monitor_fifo, daemon=True)
    thread.start()

    return app

def get_event_statistics(db, selected_event_file):
    from sqlalchemy import func, distinct
    from app.models import EventData

    # Get the number of unique drivers
    amount_drivers = db.session.query(func.count(distinct(EventData.CID))).filter(EventData.DB_FILE == selected_event_file).scalar()

    # Get the number of heats
    heat_num = db.session.query(func.max(EventData.HEAT)).filter(EventData.DB_FILE == selected_event_file).scalar() or 0

    valid_recorded_times = 0
    invalid_recorded_times = 0
    drivers_left = 0

    for heat in range(1, heat_num + 1):
        # Count valid recorded times
        valid_recorded_times += db.session.query(func.count()).filter(
            EventData.DB_FILE == selected_event_file,
            EventData.HEAT == heat,
            EventData.FINISHTIME != 0,
            EventData.PENALTY == 0
        ).scalar()

        # Count invalid recorded times
        invalid_recorded_times += db.session.query(func.count()).filter(
            EventData.DB_FILE == selected_event_file,
            EventData.HEAT == heat,
            EventData.PENALTY != 0
        ).scalar()

        # Count drivers left
        drivers_left += db.session.query(func.count()).filter(
            EventData.DB_FILE == selected_event_file,
            EventData.HEAT == heat,
            EventData.FINISHTIME == 0,
            EventData.PENALTY == 0
        ).scalar()

    event_config = {
        "all_records": (valid_recorded_times + invalid_recorded_times + drivers_left),
        "p_times": invalid_recorded_times,
        "v_times": valid_recorded_times,
        "l_times": drivers_left,
        "drivers": amount_drivers,
        "heats": heat_num
    }

    return event_config


def get_active_event_name():
    from app.lib.db_operation import get_active_event
    from app.models import EventData

    event = get_active_event()

    db_location = GetEnv()["db_location"]
    
    heat = event[0]["SPESIFIC_HEAT"]

    event_data = EventData.query.filter(
        EventData.DB_FILE == event[0]["db_file"],
        EventData.HEAT == heat
    ).first()

    event_data = {"title_1":event_data.TITLE1, "title_2":event_data.TITLE2, "heat":str(event_data.HEAT) + "/" + str(event_data.RUNS)}
    
    return event_data
