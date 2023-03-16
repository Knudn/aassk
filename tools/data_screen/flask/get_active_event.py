import sqlite3
from pathlib import Path

event_files = Path("/mnt/test/")

def get_event():
    db_path = event_files / "Online.scdb"
    event_values = []

    with sqlite3.connect(str(db_path)) as con:
        cur = con.cursor()
        cur.execute('SELECT C_VALUE FROM TPARAMETERS WHERE C_PARAM IN ("EVENT", "HEAT");')
        event_values = [row[0] for row in cur.fetchall()]
        cur.close()

    num = f"{int(event_values[0]):03}"
    return f"Event{num}.scdb", f"Event{num}Ex.scdb", event_values[1]

def get_driver_data(eventfile, heat):
    db_path = event_files / eventfile
    competitors = []
    title = "None"

    with sqlite3.connect(str(db_path)) as con:
        cur = con.cursor()
        cur.execute('SELECT C_NUM, C_FIRST_NAME, C_LAST_NAME, C_CLUB, C_TEAM FROM TCOMPETITORS;')
        competitors = cur.fetchall()
        cur.execute('SELECT C_VALUE FROM TPARAMETERS WHERE C_PARAM="TITLE2";')
        title = f"{cur.fetchone()[0]} - Run {heat}"
        cur.close()
    return title, competitors

def get_start_list(eventfile, heat):
    db_path = event_files / eventfile
    startlist = []
    finish_times = {}

    with sqlite3.connect(str(db_path)) as con:
        cur = con.cursor()
        query_startlist = f"SELECT C_NUM FROM TSTARTLIST_PARQ2_HEAT{heat};"
        query_timedata = f"SELECT C_NUM, C_TIME, C_STATUS FROM TTIMEINFOS_HEAT{heat}"

        cur.execute(query_startlist)
        startlist = [row for row in cur.fetchall()]
        cur.execute(query_timedata)
        finish_times = {row[0]: [row[1], row[2]] for row in cur.fetchall()}
        cur.close()

    paired_startlist = [(x[0], y[0]) for x, y in zip(startlist[0::2], startlist[1::2])]

    return paired_startlist, finish_times

def get_start_list_dict(startlist, competitors, time_data):
    riders = {}
    for idx, pair in enumerate(startlist):
        riders_tmp = []

        for rider_num in pair:
            for comp in competitors:
                if rider_num == comp[0]:
                    if rider_num in time_data:
                        riders_tmp.append((*comp, *time_data[rider_num], True))
                    else:
                        riders_tmp.append((*comp, 0, False, "Not Started"))

        if len(riders_tmp) < 2:
            riders_tmp.append((0, "Filler", "Filler", "Filler", "Filler", 0, False, "Not Started"))
        riders[idx] = riders_tmp

    return riders
