import sqlite3
from pathlib import Path
import json

event_files = Path("/mnt/test/")

def get_white_list():
    print("Current whitelist")
    all_evnets = []
    normal_whitelist = ['Event018', 'Event026', 'Event020', 'Event014', 'Event012', 'Event016', 'Event024', 'Event010', 'Event028', 'Event022']
    single_whitelist = ['Event019', 'Event029', 'Event025', 'Event023', 'Event011', 'Event027', 'Event015', 'Event021', 'Event013', 'Event017']
    stige_whitelist = ['Event088','Event098']

    all_evnets.extend(normal_whitelist)
    all_evnets.extend(single_whitelist)
    all_evnets.extend(stige_whitelist)


    with open("whitelist.txt","r") as outfile:
        data = json.load(outfile)
        
    return data["stige_whitelist"], data["normal_whitelist"], data["single_whitelist"]


def get_event():
    print(event_files)
    db_path = event_files / "Online.scdb"
    event_values = []
    print(db_path)
    try:
        with sqlite3.connect(str(db_path)) as con:
            cur = con.cursor()
            cur.execute('SELECT C_VALUE FROM TPARAMETERS WHERE C_PARAM IN ("EVENT", "HEAT");')
            event_values = [row[0] for row in cur.fetchall()]
            print(event_values)
            cur.close()

        num = f"{int(event_values[0]):03}"
        return f"Event{num}.scdb", f"Event{num}Ex.scdb", event_values[1]
    except:
        print("Could not get event")
        return False

def get_driver_data(eventfile, heat):
    db_path = event_files / eventfile
    competitors = []
    title = "None"
    try: 
        with sqlite3.connect(str(db_path)) as con:
            cur = con.cursor()
            cur.execute('SELECT C_NUM, C_FIRST_NAME, C_LAST_NAME, C_CLUB, C_TEAM FROM TCOMPETITORS;')
            competitors = cur.fetchall()
            cur.execute('SELECT C_VALUE FROM TPARAMETERS WHERE C_PARAM="TITLE2" OR C_PARAM="HEAT_NUMBER";')
            data = cur.fetchall()
            cur.close()
            heats = f"{data[0][0]}"
            title = f"{data[1][0]} - Run {heat}"


        return title, competitors, heats
    except:
        print("Could not get event")
        return "Error"

def get_start_list(eventfile, heat, mode, heats):
    db_path = event_files / eventfile
    startlist = []
    finish_times = {}

    with sqlite3.connect(str(db_path)) as con:
        cur = con.cursor()

        if mode == "FINALE":
            query_startlist = f"SELECT C_NUM FROM TSTARTLIST_HEAT1;"
            query_timedata = f"SELECT C_NUM, C_TIME, C_STATUS FROM TTIMEINFOS_HEAT{heat};"

        elif mode == "STIGE":
            heat_num = str((int(heats) + 1) - int(heat))
            query_startlist = f"SELECT C_NUM FROM TSTARTLIST_PARF_HEAT{heat_num};"
            query_timedata = f"SELECT C_NUM, C_TIME, C_STATUS FROM TTIMEINFOS_PARF_HEAT{heat_num}_RUN1;"
            
        else:
            query_startlist = f"SELECT C_NUM FROM TSTARTLIST_PARQ2_HEAT{heat};"
            query_timedata = f"SELECT C_NUM, C_TIME, C_STATUS FROM TTIMEINFOS_HEAT{heat};"

        cur.execute(query_startlist)
        startlist = [row for row in cur.fetchall()]

        cur.execute(query_timedata)
        finish_times = {row[0]: [row[1], row[2]] for row in cur.fetchall()}
        cur.close()

    if mode == "SINGLE":
        paired_startlist = []
        
        for a in startlist:
            paired_startlist.append(a[0])
    else: 
        paired_startlist = [(x[0], y[0]) for x, y in zip(startlist[0::2], startlist[1::2])]
    return paired_startlist, finish_times

def get_start_list_dict(startlist, competitors, time_data, mode):
    riders = {}
    for idx, pair in enumerate(startlist):
        riders_tmp = []
        if mode == "SINGLE":
            for rider_num in [pair]:
                for comp in competitors:
                    if rider_num == comp[0]:
                        if rider_num in time_data:
                            riders_tmp.append((*comp, *time_data[rider_num], True))
                            
                        else:
                            riders_tmp.append((*comp, 0, False, "Not Started"))
        else:         
            for rider_num in pair:
                for comp in competitors:
                    if rider_num == comp[0]:
                        if rider_num in time_data:
                            riders_tmp.append((*comp, *time_data[rider_num], True))
                            print((*comp, *time_data[rider_num], True))
                            print(comp)
                        else:
                            riders_tmp.append((*comp, 0, int(0), "Not Started"))
                            print((*comp, 0, 0, "Not Started"))
                            print(comp,"asd")

        if len(riders_tmp) < 2:
            riders_tmp.append((0, "Filler", "Filler", "Filler", "Filler", 0, False, "Not Started"))
        riders[idx] = riders_tmp

    return riders
