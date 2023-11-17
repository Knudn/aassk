import sqlite3
from sqlite3 import Error
import random
import os
from app.lib.utils import GetEnv
from typing import List, Dict, Union, Tuple
from datetime import datetime, timedelta

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
                    
                    cursor.execute("SELECT C_NUM, C_FIRST_NAME, C_LAST_NAME, C_CLUB, C_TEAM FROM TCOMPETITORS;")
                    driver_rows = cursor.fetchall()
                    if len(rows) >= 5:
                        print(rows)
                        if wh_check == False:
                            datevalue = timevalue_convert(int(rows[0][0]))
                            db_data.append({"db_file":filename[:-5],"MODE":rows[2][0],"TITLE1":rows[3][0],"TITLE2":rows[4][0],"HEATS":rows[0][0], "DATE":datevalue})
                            if driver_rows:
                                for b in driver_rows:
                                    driver_db_data.setdefault(filename[:-5], []).append({"CID": b[0], "FIRST_NAME": b[1], "LAST_NAME": b[2], "CLUB": b[3], "SNOWMOBILE": b[4]})
                            else:
                                pass
                        elif wh_title.upper() in str(rows[3][0]).upper():
                            datevalue = timevalue_convert(int(rows[0][0]))

                            db_data.append({"db_file":filename[:-5],"MODE":rows[2][0],"TITLE1":rows[3][0],"TITLE2":rows[4][0],"HEATS":rows[0][0], "DATE":datevalue})
                            if driver_rows and event_only == False:
                                for b in driver_rows:
                                    driver_db_data.setdefault(filename[:-5], []).append({"CID": b[0], "FIRST_NAME": b[1], "LAST_NAME": b[2], "CLUB": b[3], "SNOWMOBILE": b[4]})

    return db_data, driver_db_data

def init_database(event_files, driver_db_data, g_config, init_mode=True, exclude_lst=False):
    db_location = g_config["db_location"]
    for entry in event_files:
        with sqlite3.connect(db_location + "/" + entry["db_file"]+".sqlite") as conn:
            
            cursor = conn.cursor()
            if init_mode:
                #Create index table
                cursor.execute('''
                CREATE TABLE IF NOT EXISTS db_index (
                    MODE INTEGER,
                    RUNS INTEGER,
                    DB_FILE TEXT,
                    TITLE1 TEXT,
                    TITLE2 TEXT,
                    DATE
                )
                ''')

                cursor.execute('''
                CREATE TABLE IF NOT EXISTS drivers (
                    CID INTEGER PRIMARY KEY,
                    FIRST_NAME TEXT,
                    LAST_NAME TEXT,
                    CLUB TEXT,
                    SNOWMOBILE TEXT 
                )
                ''')

                #Replace or insert event
                cursor.execute('''
                REPLACE INTO db_index (MODE, RUNS, DB_FILE, TITLE1, TITLE2, DATE) VALUES (?, ?, ?, ?, ?, ?)
                ''', (entry["MODE"], entry["HEATS"], entry["db_file"], entry["TITLE1"], entry["TITLE2"], entry["DATE"]))

                print("Added:", entry["db_file"], entry["MODE"])

                driver_insert_data = []

                for driver_data in driver_db_data[entry["db_file"]]:
                    cid = driver_data['CID']
                    first_name = driver_data['FIRST_NAME']
                    last_name = driver_data['LAST_NAME']
                    club = driver_data['CLUB']
                    snowmobile = driver_data['SNOWMOBILE']
                    
                    driver_data_tuple = (cid, first_name, last_name, club, snowmobile)
                    driver_insert_data.append(driver_data_tuple)

                #Turning driver data into tuple
                sql = "INSERT OR IGNORE INTO drivers (CID, FIRST_NAME, LAST_NAME, CLUB, SNOWMOBILE) VALUES (?, ?, ?, ?, ?);"
                cursor.executemany(sql, driver_insert_data)

                #Add all the heats
                for a in range(0, int(entry["HEATS"])):
                    heat = (a + 1)
                    cursor.execute('''
                    CREATE TABLE IF NOT EXISTS startlist_r{0} (
                        CID_ORDER INTEGER PRIMARY KEY AUTOINCREMENT,
                        CID INTEGER,
                        FOREIGN KEY(CID) REFERENCES drivers(CID)
                    )
                    '''.format(heat))
                    
                    cursor.execute('''
                    CREATE TABLE IF NOT EXISTS driver_stats_r{0} (
                        CID INTEGER PRIMARY KEY,
                        INTER_1 INTEGER,
                        INTER_2 INTEGER,
                        INTER_3 INTEGER,
                        SPEED INTEGER,
                        PENELTY INTEGER,
                        FINISHTIME INTEGER,
                        LOCKED INTEGER DEFAULT "0" NOT NULL,
                        STATE INTEGER DEFAULT "0",
                        FOREIGN KEY(CID) REFERENCES drivers(CID)
                    )
                    '''.format(heat))
                    conn.commit()

def insert_driver_stats(db, g_config, exclude_lst=False, init_mode=True):

    from app.models import ActiveEvents
    from app import db as my_db

    event_dir = g_config["event_dir"]
    db_location = g_config["db_location"]

    for a in db:
        if "SPESIFIC_HEAT" in a.keys():
            spesific_heat = a["SPESIFIC_HEAT"]
        else:
            spesific_heat = False

        if "MODE" not in a.keys():
            mode = str(my_db.session.query(ActiveEvents.mode).filter(ActiveEvents.event_file == a["db_file"]).first()[0])
            if spesific_heat == False:
                heats = my_db.session.query(ActiveEvents).filter(ActiveEvents.event_file == a["db_file"]).count()
            else:
                heats = 1
        else:
            mode=a["MODE"]
            heats=a["HEATS"]

        local_event_db = db_location+a["db_file"]+".sqlite"
        ext_event_db = event_dir+a["db_file"]+"Ex.scdb"


        event_db_path = ext_event_db
        main_db_path = local_event_db


        for b in range(0, int(heats)):
            if spesific_heat != False:
                heat = spesific_heat
            else:
                heat = (b + 1)

            if mode == str(3):
                heat_count = my_db.session.query(ActiveEvents).filter(ActiveEvents.event_file == a["db_file"]).count()
                if spesific_heat == False:
                    heat_count = (heat_count - int(heat)) +1 
                else:
                    heat_count = (heat_count - int(heat)) +1 
                    
                query = f"SELECT C_NUM, C_INTER1, C_INTER2, C_INTER3, C_SPEED1, C_STATUS, C_TIME FROM TTIMEINFOS_PARF_HEAT{heat_count}_RUN1"
            else:
                query = f"SELECT C_NUM, C_INTER1, C_INTER2, C_INTER3, C_SPEED1, C_STATUS, C_TIME FROM TTIMEINFOS_HEAT{heat}"

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

            print(main_db_path)
            with sqlite3.connect(main_db_path) as conn:
                cursor = conn.cursor()
                sql = "SELECT * FROM startlist_r{0};".format(heat)
                startlist = cursor.execute(sql).fetchall()
                startlist_lst = [g[1] for g in startlist]

                tmp_driver = [l["CID"] for l in time_data_lst]

                for v in startlist_lst:
                    if v not in tmp_driver:
                        time_data_lst.append({
                            "CID": v, 
                            "INTER_1": 0, 
                            "INTER_2": 0, 
                            "INTER_3": 0,
                            "SPEED": 0, 
                            "PENELTY": 0, 
                            "FINISHTIME": 0
                        })

                if init_mode:

                    timedata_tuples = [
                        (d["INTER_1"], d["INTER_2"], d["INTER_3"], d["SPEED"], d["PENELTY"], d["FINISHTIME"], d["CID"]) 
                        for d in time_data_lst
                    ]
                    
                    #sql = f"""
                    #INSERT OR REPLACE INTO driver_stats_r{heat} 
                    #(INTER_1, INTER_2, INTER_3, SPEED, PENELTY, FINISHTIME, CID) 
                    #VALUES (?, ?, ?, ?, ?, ?, ?)
                    #"""
                    #cursor.executemany(sql, timedata_tuples)
                else:
                    if exclude_lst:
                        query = f"SELECT CID from driver_stats_r{str(heat)} WHERE LOCKED = 1"
                        cursor.execute(query)
                        locked_cids = [item[0] for item in cursor.fetchall()]
                        timedata_tuples = [
                            (d["INTER_1"], d["INTER_2"], d["INTER_3"], d["SPEED"], d["PENELTY"], d["FINISHTIME"], d["CID"]) 
                            for d in time_data_lst if d["CID"] not in locked_cids
                        ]

                        cursor.execute(f'DELETE FROM driver_stats_r{heat} WHERE LOCKED != 1;')
                        
                    else:
                        timedata_tuples = [
                            (d["INTER_1"], d["INTER_2"], d["INTER_3"], d["SPEED"], d["PENELTY"], d["FINISHTIME"], d["CID"]) 
                            for d in time_data_lst
                        ]
                        cursor.execute(f'DELETE FROM driver_stats_r{heat}')
                    
                sql = f"""
                INSERT OR REPLACE INTO driver_stats_r{heat} 
                (INTER_1, INTER_2, INTER_3, SPEED, PENELTY, FINISHTIME, CID) 
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """

                cursor.executemany(sql, timedata_tuples)
                    
def insert_start_list(db, g_config, init_mode=True):
    from app.models import ActiveEvents
    from app import db as my_db

    event_dir = g_config["event_dir"]
    db_location = g_config["db_location"]

    for a in db:
        if "MODE" not in a.keys():
            mode = my_db.session.query(ActiveEvents.mode).filter(ActiveEvents.event_file == a["db_file"]).first()[0]
            heats = my_db.session.query(ActiveEvents).filter(ActiveEvents.event_file == a["db_file"]).count()
        else:
            mode=a["MODE"]
            heats=a["HEATS"]

        if "SPESIFIC_HEAT" in a.keys():
            spesific_heat = a["SPESIFIC_HEAT"]
        else:
            spesific_heat = False

        local_event_db = db_location+a["db_file"]+".sqlite"
        ext_event_db = event_dir+a["db_file"]+"Ex.scdb"
        for b in range(0, int(heats)):

            heat = (b + 1)

            with sqlite3.connect(ext_event_db) as conn:
                
                cursor = conn.cursor()
                try:
                    if str(mode) == "0":
                        cursor.execute("SELECT C_NUM FROM TSTARTLIST_HEAT{0};".format(heat))

                    elif str(mode) == "2":
                        cursor.execute("SELECT C_NUM FROM TSTARTLIST_PARQ2_HEAT{0};".format(heat))

                    elif str(mode) == "3":   
                        if spesific_heat != False:
                            heat_inverted = (int(heats) - int(spesific_heat)) +1
                        else:
                            heat_inverted = (int(heats) - int(heat)) +1

                        cursor.execute("SELECT C_NUM FROM TSTARTLIST_PARF_HEAT{0};".format(heat_inverted)) 
                    else:
                        return False
                
                except Error as e:
                    print(e)
                startlist_data = cursor.fetchall()
            with sqlite3.connect(local_event_db) as conn_new_db:
                cursor_new = conn_new_db.cursor()
                if init_mode == False:
                    #NO IDEA WHY I ADDED THIS, WILL PROBABLY FIND OUT IN THE FUTURE
                    #cursor_new.execute(f'DELETE FROM driver_stats_r{heat}')
                    cursor_new.execute(f'DELETE FROM startlist_r{heat}')
                    
                try:
                    sql = "INSERT INTO startlist_r{0} (CID) VALUES (?)".format(heat)
                    cursor_new.executemany(sql, startlist_data)

                except Error as e:
                    print(e)

                conn_new_db.commit()   

