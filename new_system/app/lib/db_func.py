import sqlite3
from sqlite3 import Error
import random
import os
from app.lib.utils import GetEnv
from typing import List, Dict, Union, Tuple
from datetime import datetime, timedelta
import traceback


def timevalue_convert(dateint):

    base_date = datetime(1900, 1, 1)
    actual_date = base_date + timedelta(days=dateint - 2)
    return actual_date.strftime("%Y-%m-%d")

def map_database_files(global_config, Event=None, event_only=False):
    
    db_data = []
    driver_db_data = {}

    event_dir = global_config["event_dir"]
    wh_check = global_config["wl_bool"]
    wh_title = global_config["wl_title"]
    cross_check = global_config["cross"]
    cross_title = global_config["wl_cross_title"]
    exclude_title = global_config["exclude_title"]


    if Event != None:
        events = [Event+".scdb"]
    else:
        events = os.listdir(event_dir)

    if event_only == True:
        tmp_event_list = []

    #This for loop will enumerate a folder to find a bunch of database files

    for filename in events:
        f = os.path.join(event_dir, filename)
        # checking if it is a file
        if os.path.isfile(f):
            if "ex.scdb" not in f.capitalize() and "online" not in f.capitalize():
                with sqlite3.connect(f) as conn:
                    

                    cursor = conn.cursor()
                    cursor.execute("SELECT C_VALUE FROM TPARAMETERS WHERE C_PARAM='DATE' OR C_PARAM='MODULE' OR C_PARAM='TITLE1' OR C_PARAM='TITLE2' OR C_PARAM='HEAT_NUMBER';")
                    rows = cursor.fetchall()
                    if len(rows) <= 4:
                        continue
                    elif rows[3][0] == "COMPETITORS LIST":
                        continue
                    
                    cursor.execute("SELECT C_NUM, C_FIRST_NAME, C_LAST_NAME, C_CLUB, C_TEAM FROM TCOMPETITORS;")
                    driver_rows = cursor.fetchall()
                    if len(rows) >= 4:
                        if exclude_title.upper() in str(rows[3][0] + " " + rows[4][0]).upper() and exclude_title != "":
                            continue
                        if cross_check and str(rows[2][0]) == "0" and cross_title.upper() in str(rows[3][0] + " " + rows[4][0]).upper():
                            if wh_check and wh_title.upper() in str(rows[3][0]).upper():
                                datevalue = timevalue_convert(int(rows[0][0]))
                                db_data.append({"db_file":filename[:-5],"MODE":rows[2][0],"TITLE1":rows[3][0],"TITLE2":rows[4][0],"HEATS":rows[1][0], "DATE":datevalue})
                                if driver_rows:
                                    for b in driver_rows:
                                        driver_db_data.setdefault(filename[:-5], []).append({"CID": b[0], "FIRST_NAME": b[1], "LAST_NAME": b[2], "CLUB": b[3], "SNOWMOBILE": b[4]})
                                else:
                                    pass
                            elif wh_check == False:

                                datevalue = timevalue_convert(int(rows[0][0]))
                                db_data.append({"db_file":filename[:-5],"MODE":rows[2][0],"TITLE1":rows[3][0],"TITLE2":rows[4][0],"HEATS":rows[1][0], "DATE":datevalue})
                                if driver_rows:
                                    for b in driver_rows:
                                        driver_db_data.setdefault(filename[:-5], []).append({"CID": b[0], "FIRST_NAME": b[1], "LAST_NAME": b[2], "CLUB": b[3], "SNOWMOBILE": b[4]})
                                else:
                                    pass

                        elif wh_check == False and cross_check == False:
                            datevalue = timevalue_convert(int(rows[0][0]))
                            db_data.append({"db_file":filename[:-5],"MODE":rows[2][0],"TITLE1":rows[3][0],"TITLE2":rows[4][0],"HEATS":rows[1][0], "DATE":datevalue})
                            if driver_rows:
                                for b in driver_rows:
                                    driver_db_data.setdefault(filename[:-5], []).append({"CID": b[0], "FIRST_NAME": b[1], "LAST_NAME": b[2], "CLUB": b[3], "SNOWMOBILE": b[4]})
                            else:
                                pass

                        elif wh_title.upper() in str(rows[3][0]).upper() and cross_check == False:
                            datevalue = timevalue_convert(int(rows[0][0]))
                            db_data.append({"db_file":filename[:-5],"MODE":rows[2][0],"TITLE1":rows[3][0],"TITLE2":rows[4][0],"HEATS":rows[1][0], "DATE":datevalue})
                            if driver_rows and event_only == False:
                                for b in driver_rows:
                                    driver_db_data.setdefault(filename[:-5], []).append({"CID": b[0], "FIRST_NAME": b[1], "LAST_NAME": b[2], "CLUB": b[3], "SNOWMOBILE": b[4]})

    return db_data, driver_db_data

def insert_driver_data_to_db(event_files, driver_db_data, startlist, g_config, init_mode=True, exclude_lst=False):
    from app import db as my_db
    from app.models import EventData, CrossConfig

    cross_state = g_config["cross"]
    session = my_db.session
    cross_config = session.query(CrossConfig).first()

    if init_mode == True:
        session.query(EventData).delete()
    elif "SPESIFIC_HEAT" in event_files[0]:
        for b in event_files:
            session.query(EventData).filter(
                (EventData.HEAT == X) &
                (EventData.DB_FILE == b["asd"])
            ).delete()
    else:
        for b in event_files:
            session.query(EventData).filter(
                (EventData.DB_FILE == b["db_file"])
            ).delete()

    session.commit()

    for entry in event_files:
        db_file = entry["db_file"]
        mode = int(entry["MODE"])
        runs = int(entry["HEATS"])

        print(f"\nProcessing event: {db_file}")
        print(f"Mode: {mode}, Runs: {runs}")

        if db_file in driver_db_data and db_file in startlist:
            event_startlist = startlist[db_file]
            
            for heat in range(1, runs + 1):
                driver_results = get_driver_data(db_file, heat, mode, g_config)
                pairs = event_startlist.get(heat, [])
                
                # Flatten the pairs if they're nested
                if pairs and isinstance(pairs[0], list):
                    flat_pairs = [driver for pair in pairs for driver in pair]
                else:
                    flat_pairs = pairs

                # Process drivers
                heat_drivers = []
                if mode == 0:
                    # For mode 0, process each driver individually
                    for cid_order, cid in enumerate(flat_pairs):
                        driver_data = next((d for d in driver_db_data[db_file] if d['CID'] == cid), None)
                        if driver_data:
                            stats = next((s for s in driver_results if s['CID'] == cid), None)
                            if not stats:
                                stats = {
                                    "INTER_1": 0, "INTER_2": 0, "INTER_3": 0,
                                    "SPEED": 0, "PENELTY": 0, "FINISHTIME": 0
                                }
                                print(f"No stats found for CID {cid}. Using default values.")

                            driver_event_data = EventData(
                                MODE=mode,
                                RUNS=runs,
                                DB_FILE=db_file,
                                TITLE1=entry["TITLE1"],
                                TITLE2=entry["TITLE2"],
                                DATE=datetime.strptime(entry["DATE"], "%Y-%m-%d"),
                                CID=cid,
                                FIRST_NAME=driver_data['FIRST_NAME'],
                                LAST_NAME=driver_data['LAST_NAME'],
                                CLUB=driver_data['CLUB'],
                                SNOWMOBILE=driver_data['SNOWMOBILE'],
                                HEAT=heat,
                                PAIR=cid_order + 1,  # Each driver is their own "pair" in mode 0
                                CID_ORDER=1,  # Always 1 in mode 0 as each driver is processed individually
                                INTER_1=stats['INTER_1'],
                                INTER_2=stats['INTER_2'],
                                INTER_3=stats['INTER_3'],
                                SPEED=stats['SPEED'],
                                PENALTY=stats['PENELTY'],
                                FINISHTIME=stats['FINISHTIME'],
                                LOCKED=0,
                                STATE=0,
                                POINTS=0
                            )
                            heat_drivers.append(driver_event_data)
                            print(f"Added driver: CID {cid}, Order {cid_order + 1}")
                        else:
                            print(f"No driver data found for CID {cid}")
                else:
                    # For other modes, process drivers in pairs as before
                    for i in range(0, len(flat_pairs), 2):
                        pair = flat_pairs[i:i+2]
                        
                        for cid_order, cid in enumerate(pair):
                            driver_data = next((d for d in driver_db_data[db_file] if d['CID'] == cid), None)
                            if driver_data:
                                stats = next((s for s in driver_results if s['CID'] == cid), None)
                                if not stats:
                                    stats = {
                                        "INTER_1": 0, "INTER_2": 0, "INTER_3": 0,
                                        "SPEED": 0, "PENELTY": 0, "FINISHTIME": 0
                                    }
                                    print(f"No stats found for CID {cid}. Using default values.")

                                driver_event_data = EventData(
                                    MODE=mode,
                                    RUNS=runs,
                                    DB_FILE=db_file,
                                    TITLE1=entry["TITLE1"],
                                    TITLE2=entry["TITLE2"],
                                    DATE=datetime.strptime(entry["DATE"], "%Y-%m-%d"),
                                    CID=cid,
                                    FIRST_NAME=driver_data['FIRST_NAME'],
                                    LAST_NAME=driver_data['LAST_NAME'],
                                    CLUB=driver_data['CLUB'],
                                    SNOWMOBILE=driver_data['SNOWMOBILE'],
                                    HEAT=heat,
                                    PAIR=i//2 + 1,
                                    CID_ORDER=cid_order + 1,
                                    INTER_1=stats['INTER_1'],
                                    INTER_2=stats['INTER_2'],
                                    INTER_3=stats['INTER_3'],
                                    SPEED=stats['SPEED'],
                                    PENALTY=stats['PENELTY'],
                                    FINISHTIME=stats['FINISHTIME'],
                                    LOCKED=0,
                                    STATE=0,
                                    POINTS=0
                                )
                                heat_drivers.append(driver_event_data)
                                print(f"Added driver: CID {cid}, Pair {i//2 + 1}, Order {cid_order + 1}")
                            else:
                                print(f"No driver data found for CID {cid}")

                # Assign points for the heat
                if cross_state:
                    assign_points_for_heat(heat_drivers, cross_config)

                # Add all drivers for this heat to the session
                session.add_all(heat_drivers)

            print(f"Finished processing event: {db_file}")
        else:
            print(f"No driver data or start list found for event: {db_file}")

    session.commit()
    print("Database initialization completed.")


def assign_points_for_heat(drivers, cross_config):
    
    valid_drivers = []
    penalized_drivers = []

    for driver in drivers:
        print(driver.TITLE2)
        if "fellesstart" in driver.TITLE2.lower(): 
            if driver.PENALTY == 0 and int(driver.FINISHTIME) > 0:
                valid_drivers.append(driver)
            elif int(driver.PENALTY) != 0:
                penalized_drivers.append(driver)

            

    # Sort valid drivers by finish time
    valid_drivers.sort(key=lambda driver: driver.FINISHTIME)

    # Assign points to valid drivers based on their finish position
    for position, driver in enumerate(valid_drivers, start=1):
        position_str = str(position)
        if position_str in cross_config.driver_scores:
            driver.POINTS = cross_config.driver_scores[position_str]
        else:
            driver.POINTS = 0  # No points for positions beyond those specified

    # Assign points to penalized drivers based on their state
    for driver in penalized_drivers:
        print(driver.PENALTY)
        if int(driver.PENALTY) == 2:
            driver.POINTS = cross_config.dnf_point  # DNF (Did Not Finish)
        elif int(driver.PENALTY) == 1:
            driver.POINTS = cross_config.dns_point  # DNS (Did Not Start)
        elif int(driver.PENALTY) == 3:
            driver.POINTS = cross_config.dsq_point  # DSQ (Disqualified)
        else:
            driver.POINTS = 0  # Default to 0 points for unknown states

    # Invert scores if specified in CrossConfig
    if cross_config.invert_score:
        max_points = max(driver.POINTS for driver in drivers)
        for driver in drivers:
            driver.POINTS = max_points - driver.POINTS

    return drivers

def get_driver_data(event, heat, mode, g_config):
    from app import db as my_db
    from app.models import ActiveEvents

    event_dir = g_config["event_dir"]
    db_location = g_config["db_location"]


    event_db_path = event_dir + event + "Ex.scdb"

    if g_config["cross"] and mode == int(0):

        query = f"SELECT t2.C_NUM, t2.C_HOUR2, COALESCE(t1.C_INTER2, 0) AS C_INTER2, COALESCE(t1.C_INTER3, 0) AS C_INTER3, COALESCE(t1.C_SPEED1, 0) AS C_SPEED1, COALESCE(t1.C_STATUS, 0) AS C_STATUS, COALESCE(t1.C_TIME, 0) AS C_TIME FROM TTIMERECORDS_HEAT{heat}_START t2 LEFT JOIN TTIMEINFOS_HEAT{heat} t1 ON t2.C_NUM = t1.C_NUM"

    elif mode == int(3):
        heat_count = my_db.session.query(ActiveEvents).filter(ActiveEvents.event_file == event).count()

        heat_count = (heat_count - int(heat)) + 1 
        query = f"SELECT C_NUM, C_INTER1, C_INTER2, C_INTER3, C_SPEED1, C_STATUS, C_TIME FROM TTIMEINFOS_PARF_HEAT{heat_count}_RUN1"
    else:
        query = f"SELECT C_NUM, C_INTER1, C_INTER2, C_INTER3, C_SPEED1, C_STATUS, C_TIME FROM TTIMEINFOS_HEAT{heat}"

    time_data_lst = []

    try:
        with sqlite3.connect(event_db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(query)
            time_data = cursor.fetchall()

            time_data_lst = [
                {
                    "CID": data[0], "INTER_1": data[1], "INTER_2": data[2], "INTER_3": data[3],
                    "SPEED": data[4], "PENELTY": data[5], "FINISHTIME": data[6]
                } 
                for data in time_data
            ]
    except sqlite3.Error as e:
        print(f"SQLite error occurred while fetching data for event {event}, heat {heat}: {e}")
    except Exception as e:
        print(f"An error occurred while processing data for event {event}, heat {heat}: {e}")

    if not time_data_lst:
        print(f"No time data found for event {event}, heat {heat}")

    return time_data_lst


def get_start_list(db_data ,g_config, init_mode=True):
    from app.models import ActiveEvents
    from app import db as my_db

    event_dir = g_config["event_dir"]
    db_location = g_config["db_location"]

    startlist_dict = {}

    for a in db_data:
        mode=a["MODE"]
        heats=a["HEATS"]

        if "SPESIFIC_HEAT" in a.keys():
            spesific_heat = a["SPESIFIC_HEAT"]
        else:
            spesific_heat = False

        local_event_db = db_location+a["db_file"]+".sqlite"
        ext_event_db = event_dir+a["db_file"]+"Ex.scdb"

        startlist_dict[a["db_file"]] = {}

        for b in range(0, int(heats)):
            heat = (b + 1)
            startlist_dict[a["db_file"]][heat] = []
            with sqlite3.connect(ext_event_db) as conn:
                
                cursor = conn.cursor()
                try:
                    if str(mode) == "0":
                        cursor.execute("SELECT C_NUM FROM TSTARTLIST_HEAT{0};".format(heat))

                    elif str(mode) == "2":

                        cursor.execute("SELECT C_NUM FROM TSTARTLIST_PARQ2_HEAT{0};".format(heat))

                    elif str(mode) == "3":   
                        
                        if spesific_heat != False:
                            heat_inverted = (int(heats) - int(heat)) +1
                            
                        else:
                            heat_inverted = (int(heats) - int(heat)) +1

                        cursor.execute("SELECT C_NUM FROM TSTARTLIST_PARF_HEAT{0};".format(heat_inverted)) 
                    else:
                        return False
                
                except Error as e:
                    print(e)
                startlist_data = cursor.fetchall()

                if len(startlist_data) == 0:
                    print("No drivers")
                    continue

            if int(mode) == 2:
                for d1, d2 in zip(*[iter(startlist_data)]*2):
                    startlist_dict[a["db_file"]][heat].append([d1[0], d2[0]])
            elif int(mode) == 0:
                for d1 in startlist_data:
                    startlist_dict[a["db_file"]][heat].append([d1[0]])

    return startlist_dict

