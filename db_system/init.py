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

                try:
                    if wh_check == False:
                        db_data.append({"db_file":filename[:-5],"MODE":rows[1][0],"TITLE1":rows[2][0],"TITLE2":rows[3][0],"HEATS":rows[0][0]})
                    elif wh_title.upper() in str(rows[1][0]).upper():
                        db_data.append({"db_file":filename[:-5],"MODE":rows[1][0],"TITLE1":rows[2][0],"TITLE2":rows[3][0],"HEATS":rows[0][0]})
                except:
                    pass
                cursor.close()
                conn.close()
    return db_data

def update_db(db_data, heat=False):

    def create_index_table(entry):

        conn = sqlite3.connect(db_location + "/" + entry["db_file"]+".sqlite")
        cursor = conn.cursor()
        
        cursor.execute('''
        DROP TABLE IF EXISTS db_index;
        ''')

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
            ID INTEGER PRIMARY KEY,
            CID INTEGER,
            FIRST_NAME TEXT,
            LAST_NAME TEXT,
            TITLE2 TEXT
        )
        ''')
        cursor.execute('''
        INSERT INTO db_index (MODE, RUNS, DB_FILE, TITLE1, TITLE2) VALUES (?, ?, ?, ?, ?)
        ''', (entry["MODE"], entry["HEATS"], entry["db_file"], entry["TITLE1"], entry["TITLE2"]))        
        conn.commit()
        conn.close()
    def insert_heat(db_file, heat):
        file = event_dir + db_file + "Ex.scdb"

    def get_db_data(db_file, heat, mode):
        file = event_dir + db_file + "Ex.scdb"
        conn = sqlite3.connect('racing.db')
        cursor = conn.cursor()

        cursor.execute("SELECT C_VALUE FROM TPARAMETERS WHERE C_PARAM='MODULE' OR C_PARAM='TITLE1' OR C_PARAM='TITLE2' OR C_PARAM='HEAT_NUMBER';")
        rows = cursor.fetchall()
        cursor.close()
        conn.close()

    if type(db_data) == list:
        for a in db_data:
            create_index_table(a)
            for b in range(1,int(a["HEATS"])):
                get_db_data(a["db_file"], b, a["MODE"])
                insert_heat(a["db_file"], b)

    elif heat != False:
        print("asd")


db_data = map_database_files(event_dir, wh_check=False)

heat=1

update_db(db_data, heat)


