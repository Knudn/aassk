import sqlite3

event_files = "/mnt/test/"

def get_event():
    # Create a SQL connection to our SQLite database
    con = sqlite3.connect(event_files+"Online.scdb")
    cur = con.cursor()
    # The result of a "cursor.execute" can be iterated over by row
    for row in cur.execute('SELECT C_VALUE FROM TPARAMETERS WHERE C_PARAM="EVENT";'):
        con.commit()

        if int(row[0]) < 9:
            num = "00"+row[0]
            return "Event"+num+".scdb", "Event"+num+"Ex.scdb"
        elif int(row[0]) < 99:
            num = "0"+row[0]
            return "Event"+num+".scdb", "Event"+num+"Ex.scdb"
        else:
            num = row[0]
            return "Event"+num+".scdb", "Event"+num+"Ex.scdb"

    # Be sure to close the connection
    con.close()

def get_driver_data(eventfile):
    com_list = []
    title = "None"
    con = sqlite3.connect(event_files+eventfile)
    cur = con.cursor()
    for row in cur.execute('SELECT C_NUM, C_FIRST_NAME, C_LAST_NAME, C_CLUB, C_TEAM FROM TCOMPETITORS;'):
        com_list.append(row)
    for row in cur.execute('SELECT C_VALUE FROM TPARAMETERS WHERE C_PARAM="TITLE2";'):
        title = row[0]
    con.commit()
    con.close()

    
    return title, com_list

def get_start_list(eventfile):
    startlist = []
    finish_times = {}

    title = "Run 1"
    con = sqlite3.connect(event_files+eventfile)
    cur = con.cursor()
    for row in cur.execute('SELECT C_NUM FROM TSTARTLIST_PARQ2_HEAT1;'):
        startlist.append(row)
    for row in cur.execute('SELECT C_NUM, C_TIME, C_STATUS FROM TTIMEINFOS_HEAT1;'):
        finish_times[row[0]] = [row[1], row[2]]

    paired_startlist = [(x[0], y[0]) for x, y in zip(startlist[0::2], startlist[1::2])]

    return paired_startlist, finish_times

def get_start_list_dict(startlist,con_per,time_data):
    riders = {}
    
    for v,a in enumerate(startlist):
        riders_tmp = []
        for g in a:
            other_data = ""
            for n in con_per:
                if g == n[0]:
                    found = False
                    for k in time_data:
                        if k == n[0]:
                            riders_tmp.append((n[0],n[1],n[2],n[4],n[3],time_data[k][0],True,time_data[k][1]))
                            found = True
                    if found == False:
                        riders_tmp.append((n[0],n[1],n[2],n[4],n[3],0,False,"Not Started"))

        if len(riders_tmp) < 2:
            riders_tmp.append((0,"Filler", "Filler","Filler","Filler",0,False,"Not Started",))
        riders[v] = riders_tmp

    return riders