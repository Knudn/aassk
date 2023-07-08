from datetime import datetime
import sqlite3
from pathlib import Path
import os

event_files = Path("/share/msport_events/Events")

def convert_time_to_microseconds(time_string):
    # split the time_string into hours, minutes, seconds and milliseconds
    parts = time_string.split(':')
    hours = int(parts[0].split('h')[0])
    minutes = int(parts[0].split('h')[1])
    seconds, milliseconds = parts[1].split(".")
    seconds = int(seconds)
    milliseconds = int(str(milliseconds)) # This line has been updated
    # convert hours, minutes, seconds and milliseconds to microseconds
    microseconds = ((hours * 60 * 60 + minutes * 60 + seconds) * 1000) * 1000 + milliseconds 

    return round(microseconds) # This line has been updated

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


# Test
# Get current date and time
current_datetime = datetime.now()
# Format the datetime as desired
formatted_datetime = current_datetime.strftime("%Hh%M:%S.%f")

data = convert_time_to_microseconds(formatted_datetime)
while True:
        # Get current date and time
        current_datetime = datetime.now()
        # Format the datetime as desired
        formatted_datetime = current_datetime.strftime("%Hh%M:%S.%f")
        asd = convert_time_to_microseconds("00h05:00.343000")
        main = (asd - data)
        print(300343000,"asd")
        print(asd, "added")
        print(300343000)
        
        print(convert_microseconds_to_time(1361846040))
        input()
        
