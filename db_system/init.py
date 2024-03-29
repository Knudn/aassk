import sqlite3
from sqlite3 import Error
import random
import os
from envbash import load_envbash

load_envbash('/home/rock/aassk/global_config.sh')
event_dir = os.environ["aassk_event_dir"]+"/"
db_location = os.environ["aassk_db_location"]+"/"
wh_title = os.environ["aassk_wl_title"]


def map_database_files(event_dir,wh_check=False):

    db_data = []
    driver_db_data = {}

    #This for loop will enumerate a folder to find a bunch of database files
    for filename in os.listdir(event_dir):
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

def update_db(db_data, driver_db_data,heat=False):

    def init_database(entry, driver_db_data):

        conn = sqlite3.connect(db_location + "/" + entry["db_file"]+".sqlite")
        #conn = sqlite3.connect("/mnt/test/db_test/" + entry["db_file"]+".sqlite")
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
                FOREIGN KEY(CID) REFERENCES drivers(CID)
            )
            '''.format(heat))
            conn.commit()
            try:
                insert_start_list(entry["db_file"], heat, entry["MODE"])
                insert_driver_stats(entry["db_file"], heat)

            except:
                pass

        conn.close()              

    def insert_start_list(db, heat, mode):
        
        #List used later down the line
        conn = sqlite3.connect(event_dir + db+"Ex.scdb")
        cursor = conn.cursor()

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
        
    if type(db_data) == list:

        for a in db_data: 
            if a["db_file"] in driver_db_data:
                init_database(a, driver_db_data[a["db_file"]])
            else:
                init_database(a, None)

    elif heat != False:
        print("asd")

def insert_driver_stats(db, heat, exclude_lst=False):
    
    exclude_lst = ["23","33"]

    conn = sqlite3.connect(event_dir + db+"Ex.scdb")
    cursor = conn.cursor()
    cursor.execute("SELECT C_NUM, C_INTER1, C_INTER2, C_INTER3, C_SPEED1, C_PENALTY, C_TIME FROM TTIMEINFOS_HEAT{0};".format(heat))
    time_data = cursor.fetchall()
    
    time_data_lst = []
    for a in time_data:
        print(a)
        time_data_lst.append({"CID":a[0],"INTER_1":a[1],"INTER_2":a[2],"INTER_3":a[3],"SPEED":a[4],"PENELTY":a[5],"FINISHTIME":a[6]})

    conn.commit()
    conn.close()

    timedata_tuples = [(d["CID"], d["INTER_1"], d["INTER_2"], d["INTER_3"],d["SPEED"],d["PENELTY"],d["FINISHTIME"]) for d in time_data_lst]

    conn = sqlite3.connect(db_location + db +".sqlite")
    cursor = conn.cursor()

    sql = "INSERT INTO driver_stats_r{0} (CID, INTER_1, INTER_2, INTER_3, SPEED, PENELTY, FINISHTIME) VALUES (?, ?, ?, ?, ?, ?, ?)".format(heat)
    cursor.executemany(sql, timedata_tuples)
    
    conn.commit()
    conn.close()


db_data, driver_db_data = map_database_files(event_dir, wh_check=False)

heat=1

update_db(db_data, driver_db_data)


