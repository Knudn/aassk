import sqlite3
from sqlite3 import Error
import random
import os
from app.lib.utils import GetEnv
from typing import List, Dict, Union, Tuple


def map_database_files(g_conf, event_file=False):
    
    db_data = []
    driver_db_data = {}

    event_dir = g_conf["event_dir"]
    wh_check = g_conf["wl_bool"]
    wh_title = g_conf["wl_title"]
    if event_file == False:
        events = os.listdir(event_dir)
    else:
        events = [(event_file+".scdb")]

    #This for loop will enumerate a folder to find a bunch of database files
    for filename in events:
        f = os.path.join(event_dir, filename)
        # checking if it is a file
        if os.path.isfile(f):
            if "ex.scdb" not in f.capitalize() and "online" not in f.capitalize():
                conn = sqlite3.connect(f)
                cursor = conn.cursor()
                cursor.execute("SELECT C_VALUE FROM TPARAMETERS WHERE C_PARAM='MODULE' OR C_PARAM='TITLE1' OR C_PARAM='TITLE2' OR C_PARAM='HEAT_NUMBER';")
                rows = cursor.fetchall()

                cursor.execute("SELECT C_NUM, C_FIRST_NAME, C_LAST_NAME, C_CLUB, C_TEAM FROM TCOMPETITORS;")
                driver_rows = cursor.fetchall()
                if len(rows) >= 4:
                    if wh_check == False:
                        db_data.append({"db_file":filename[:-5],"MODE":rows[1][0],"TITLE1":rows[2][0],"TITLE2":rows[3][0],"HEATS":rows[0][0]})
                        if driver_rows:
                            for b in driver_rows:
                                driver_db_data.setdefault(filename[:-5], []).append({"CID": b[0], "FIRST_NAME": b[1], "LAST_NAME": b[2], "CLUB": b[3], "SNOWMOBILE": b[4]})
                        else:
                            pass
                    elif wh_title.upper() in str(rows[2][0]).upper():
                        db_data.append({"db_file":filename[:-5],"MODE":rows[1][0],"TITLE1":rows[2][0],"TITLE2":rows[3][0],"HEATS":rows[0][0]})
                        if driver_rows:
                            for b in driver_rows:
                                driver_db_data.setdefault(filename[:-5], []).append({"CID": b[0], "FIRST_NAME": b[1], "LAST_NAME": b[2], "CLUB": b[3], "SNOWMOBILE": b[4]})
                        else:
                            pass

                cursor.close()
                conn.close()


    return db_data, driver_db_data

def update_db(db_data, driver_db_data, g_config, event_heat=False):
    
    if type(db_data) == list:
        try:
            for a in db_data: 
                if a["db_file"] in driver_db_data:
                    init_database(a, driver_db_data[a["db_file"]], g_config)
                else:
                    init_database(a, None)
        except:
            pass

def get_active_data(g_conf):

    event_dir = g_conf["event_dir"]

    with sqlite3.connect(event_dir+"Online.scdb") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT C_VALUE FROM TPARAMETERS WHERE C_PARAM='EVENT' OR C_PARAM='HEAT';")
        rows = cursor.fetchall()

    return rows[0][0], rows[1][0]

def init_database(entry, driver_db_data, g_config):
    db_location = g_config["db_location"]

    conn = sqlite3.connect(db_location + "/" + entry["db_file"]+".sqlite")
    cursor = conn.cursor()

    #Create index table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS db_index (
        MODE INTEGER,
        RUNS INTEGER,
        DB_FILE TEXT,
        TITLE1 TEXT,
        TITLE2 TEXT
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

    cursor.execute('''
    INSERT INTO db_index (MODE, RUNS, DB_FILE, TITLE1, TITLE2) VALUES (?, ?, ?, ?, ?)
    ''', (entry["MODE"], entry["HEATS"], entry["db_file"], entry["TITLE1"], entry["TITLE2"]))

    if driver_db_data != None:
        print("Added:", entry["db_file"], entry["MODE"])
        driver_insert_data = [(entry['CID'], entry['FIRST_NAME'], entry['LAST_NAME'], entry['CLUB'], entry['SNOWMOBILE']) for entry in driver_db_data]
        sql = "INSERT INTO drivers (CID, FIRST_NAME, LAST_NAME, CLUB, SNOWMOBILE) VALUES (?, ?, ?, ?, ?)"
        cursor.executemany(sql, driver_insert_data)

    for a in range(0, int(entry["HEATS"])):
        heat = (a + 1)

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS startlist_r{0} (
            CID_ORDER INTEGER PRIMARY KEY AUTOINCREMENT,
            CID_D1 INTEGER,
            CID_D2 INTEGER,
            FOREIGN KEY(CID_D1) REFERENCES drivers(CID),
            FOREIGN KEY(CID_D2) REFERENCES drivers(CID)
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
            FOREIGN KEY(CID) REFERENCES drivers(CID)
        )
        '''.format(heat))
        conn.commit()
        try:
            insert_start_list(entry["db_file"], heat, entry["MODE"], g_config)
            insert_driver_stats(entry["db_file"], heat, g_config)

        except:
            pass

    conn.close()              

def insert_start_list(db, heat, mode, g_config):
    event_dir = g_config["event_dir"]
    db_location = g_config["db_location"]
    #List used later down the line
    conn = sqlite3.connect(event_dir + db+"Ex.scdb")
    cursor = conn.cursor()
    print(heat)
    try:
        if mode == "0":
            cursor.execute("SELECT C_NUM FROM TSTARTLIST_HEAT{0};".format(heat))

        elif mode == "2":
            cursor.execute("SELECT C_NUM FROM TSTARTLIST_PARQ2_HEAT{0};".format(heat))

        elif mode == "3":
            cursor.execute("SELECT C_NUM FROM TSTARTLIST_PARF_HEAT{0};".format(heat)) 
        else:
            return False
        
    except Error as e:
        print(e)

    startlist_data = cursor.fetchall()

    conn_new_db = sqlite3.connect(db_location + db +".sqlite")
    cursor_new = conn_new_db.cursor()

    count = 0
    startlist_list = []
    for k,a in enumerate(startlist_data):
        if (k % 2):
            D2 = a[0]
            startlist_list.append({"CID_D1":D1, "CID_D2":D2})
        else:
            D1 = a[0]
    try:
        sql = "INSERT INTO startlist_r{0} (CID_D1, CID_D2) VALUES (?, ?)".format(heat)
        startlist_tuples = [(d["CID_D1"], d["CID_D2"]) for d in startlist_list]

        cursor_new.executemany(sql, startlist_tuples)

    except Error as e:
        print(e)

    conn_new_db.commit()
    conn_new_db.close()
    


def insert_driver_stats(
    db: str, 
    heat: int, 
    g_config: Dict[str, str], 
    exclude_lst: bool = False, 
    init_mode: bool = True
) -> None:
    from app.models import ActiveEvents
    from app import db as my_db

    mode = my_db.session.query(ActiveEvents.mode).filter(ActiveEvents.event_file == db).first()[0]
    
    
    event_dir = g_config["event_dir"]
    db_location = g_config["db_location"]
    event_db_path = f"{event_dir}{db}Ex.scdb"
    main_db_path = f"{db_location}{db}.sqlite"
    
    if mode == 3:
        query = f"SELECT C_NUM, C_INTER1, C_INTER2, C_INTER3, C_SPEED1, C_PENALTY, C_TIME FROM TTIMEINFOS_PARF_HEAT{heat}_RUN1"
    else:
        query = f"SELECT C_NUM, C_INTER1, C_INTER2, C_INTER3, C_SPEED1, C_PENALTY, C_TIME FROM TTIMEINFOS_HEAT{heat}"
    with sqlite3.connect(event_db_path) as conn:
        cursor = conn.cursor()
        print(query)
        cursor.execute(query)
        time_data = cursor.fetchall()

    time_data_lst = [
        {
            "CID": data[0], "INTER_1": data[1], "INTER_2": data[2], "INTER_3": data[3],
            "SPEED": data[4], "PENELTY": data[5], "FINISHTIME": data[6]
        } 
        for data in time_data
    ]

    with sqlite3.connect(main_db_path) as conn:
        cursor = conn.cursor()
        if init_mode:
            timedata_tuples = [
                (d["INTER_1"], d["INTER_2"], d["INTER_3"], d["SPEED"], 1, d["FINISHTIME"], d["CID"]) 
                for d in time_data_lst
            ]
            sql = f"INSERT INTO driver_stats_r{heat} (INTER_1, INTER_2, INTER_3, SPEED, PENELTY, FINISHTIME, CID) VALUES (?, ?, ?, ?, ?, ?, ?)"
        else:
            if exclude_lst:
                query = f"SELECT CID from driver_stats_r{heat} WHERE LOCKED = 1"
                cursor.execute(query)
                locked_cids = [item[0] for item in cursor.fetchall()]
                timedata_tuples = [
                    (d["INTER_1"], d["INTER_2"], d["INTER_3"], d["SPEED"], d["PENELTY"], d["FINISHTIME"], 0, d["CID"]) 
                    for d in time_data_lst if d["CID"] not in locked_cids
                ]
            else:
                timedata_tuples = [
                    (d["INTER_1"], d["INTER_2"], d["INTER_3"], d["SPEED"], d["PENELTY"], d["FINISHTIME"], 0, d["CID"]) 
                    for d in time_data_lst
                ]
            sql = f"""
            UPDATE driver_stats_r{heat}
            SET INTER_1 = ?, INTER_2 = ?, INTER_3 = ?, SPEED = ?, PENELTY = ?, FINISHTIME = ?, LOCKED = ?
            WHERE CID = ?
            """
        
        cursor.executemany(sql, timedata_tuples)

def delete_events(directory_path):
    files = os.listdir(directory_path)
    
    for file in files:
        file_path = os.path.join(directory_path, file)
        
        if os.path.isfile(file_path):
            os.remove(file_path)


def full_db_reload():
    from app.models import ActiveEvents
    from app import db


    g_config = GetEnv()

    delete_events(g_config["db_location"])
    
    db_data, driver_db_data = map_database_files(g_config)
    for a in db_data:
        print(a)
    ActiveEvents.query.delete()

    count = 0
    for a in db_data:
        for b in range(1, (int(a['HEATS']) + 1)):
            count += 1
            event_entry = ActiveEvents(event_name=(a["TITLE1"] + " " + a["TITLE2"]), run=b, sort_order=count, event_file=a["db_file"], mode=a["MODE"])
            db.session.add(event_entry)

    db.session.commit()
        
    update_db(db_data, driver_db_data, g_config)

def reload_event(db, heat):
    g_config = GetEnv()
    insert_driver_stats(db, heat, g_config, init_mode=False, exclude_lst=False)

def update_event(db, heat):
    g_config = GetEnv()
    insert_driver_stats(db, heat, g_config, init_mode=False, exclude_lst=True)

def update_active_event_stats():
    g_config = GetEnv()
    event, heat = update_active_event()
    event = "Event"+event
    insert_driver_stats(event, heat, g_config, init_mode=False, exclude_lst=True)    
    
def update_active_event():
    from app.models import ActiveDrivers
    from app import db

    g_config = GetEnv()

    data = ActiveDrivers.query.get(1)
    event, heat = get_active_data(g_config)
    event = str(event).zfill(3)

    if data:
        data.Event = event
        data.Heat = heat

    db.session.commit()
    return event, heat
    


