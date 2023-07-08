from datetime import datetime
import sqlite3
from pathlib import Path
import os
import re


event_files_new = []

event_files = Path("/share/msport_timing_check/")


def convert_to_microseconds(timestamp):
    # Splitting the timestamp
    parts = timestamp.replace('h', ':').split(':')
    hours, minutes, seconds = map(float, parts)

    # Convert hours and minutes to seconds and add them
    total_seconds = hours * 3600 + minutes * 60 + seconds

    # Convert to microseconds
    microseconds = total_seconds * 1e6

    return microseconds

def convert_microseconds_to_time(microseconds):
    # convert microseconds to milliseconds
    milliseconds = microseconds / 1000

    # convert milliseconds to seconds
    seconds = milliseconds / 1000

    # convert seconds to minutes
    minutes = seconds / 60

    # convert minutes to hours
    hours = minutes / 60

    # calculate each unit and the remainder
    hours, rem = divmod(hours, 1)
    minutes, rem = divmod(rem * 60, 1)
    seconds, rem = divmod(rem * 60, 1)
    milliseconds = rem * 1000

    # return a string in the format "hours:minutes:seconds.milliseconds"
    return "{:02d}h{:02d}:{:02.5f}".format(int(hours), int(minutes), seconds + milliseconds/1000)




def get_file_number(filename):
    # Extract the number from the file name using regular expressions
    match = re.search(r'\d+', filename)
    if match:
        return int(match.group())
    else:
        return 0  # Return 0 if no number is found

driver_times = {}
count = 0


def get_driver_data(eventfile,count):
    driver_times[count] = []
    db_path = event_files / eventfile
    num = 1
    try: 
        with sqlite3.connect(str(db_path), isolation_level='EXCLUSIVE') as con:
            cur = con.cursor()
            try:
                cur.execute("SELECT C_MESSAGE FROM TCHRONOMESSAGES_PARF_HEAT1 WHERE C_CANAL='1';")
                data = cur.fetchall()
                cur.close()

                if data == "[]":
                    pass
                else:
                    driver_times[count].append({num:data[0]})
                         
            except:
                cur.execute("SELECT C_MESSAGE FROM TCHRONOMESSAGES_PARQ2_HEAT1 WHERE C_CANAL='1';")
                data = cur.fetchall()
                cur.close()

                if data == "[]":
                    pass
                else:
                    driver_times[count].append({num:data[0]})
    
    except:
        pass

def get_driver_data_new(eventfile,count):
    
    db_path = event_files / eventfile
    num = 2
    try: 
        with sqlite3.connect(str(db_path), isolation_level='EXCLUSIVE') as con:
            cur = con.cursor()
            try:
                cur.execute("SELECT C_MESSAGE FROM TCHRONOMESSAGES_PARF_HEAT1 WHERE C_CANAL='1+';")
                data = cur.fetchall()
                cur.close()

                if data == "[]":
                    pass
                else:
                    driver_times[count].append({num:data[0]})
                         
            except:
                cur.execute("SELECT C_MESSAGE FROM TCHRONOMESSAGES_PARQ2_HEAT1 WHERE C_CANAL='1+';")
                data = cur.fetchall()
                cur.close()

                if data == "[]":
                    pass
                else:
                    driver_times[count].append({num:data[0]})

    except:
        pass



for filename in os.listdir(event_files):
    file_path = os.path.join(event_files, filename)
    if os.path.isfile(file_path):
        # Process the file here
        if filename == "Online.scdb":
            pass
        elif "Ex" in filename:
            event_files_new.append(filename)
        else:
            pass



# Sort the list based on the custom sorting key
sorted_list = sorted(event_files_new, key=get_file_number)
for a in sorted_list:

    get_driver_data(a,a[5:][:3])
    get_driver_data_new(a,a[5:][:3])

data = {k: v for k, v in driver_times.items() if len(v) >= 2}

print(data)