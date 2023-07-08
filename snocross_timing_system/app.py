import time
from flask import Flask, render_template,request, session
from get_active_event import *
import json
import sqlite3
import os

def get_event_data():

    eventfile, eventex, heat = get_event()
    event_heat = [eventfile, eventex, heat]
    # Save current event data to a file
    
    con_title, con_per, heats = get_driver_data(eventfile, heat)

    mode_title = con_title.upper()

    if "STIGE" in mode_title:
        mode = "STIGE"
    ##IF IT IS A SINGLE TRACK IT WILL APPLY THESE CONFIGURATIONS
    elif "FINALE" in mode_title:
        mode = "FINALE"
    else:
        mode = "PARALLEL"

    with open("startlist/current.json", "w") as outfile:
        json.dump(event_heat, outfile)

    startlist, time_data = get_start_list(eventex, heat, mode, heats)

    start_list_dict = get_start_list_dict(startlist, con_per, time_data,mode)

    # Save start list dictionary to a file
    with open("startlist/" + eventfile + "_" + heat + "_" + ".json", "w") as outfile:

        json.dump(start_list_dict, outfile)

    # Save driver list to a file
    with open("startlist/" + eventex + "_" + heat + "_title_.json", "w") as outfile:
        outfile.write(con_title)
        
    # Return the start list dictionary, driver list and eventex
    return start_list_dict, con_title, eventex
    
# Call the get_event_data function to fetch the event data and save it to files
start_list_dict, con_title, eventex = get_event_data()


app = Flask(__name__)

@app.route("/new_event")
def new_event():
    get_event_data()
    return "Updated event"

@app.route('/timestamp', methods=['GET'])
def get_timestamp():
    driver_id = request.json.get('driver_id', None)
    if driver_id is None:
        return "asd"

    timestamp = time.time()
    return "asd"

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5555)
