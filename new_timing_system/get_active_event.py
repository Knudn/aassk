import sqlite3
from pathlib import Path
import json
import os
import datetime
from flask import Response
import re

point_weight = [9,6,4,2]

def convert_microseconds_to_time(microseconds):
    # convert microseconds to seconds
    seconds = microseconds / 1_000_000

    # calculate each unit and the remainder
    hours, rem = divmod(seconds, 3600)
    minutes, rem = divmod(rem, 60)
    seconds, rem = divmod(rem, 1)
    milliseconds = rem * 1000

    # return a string in the format "hours:minutes:seconds.milliseconds"
    return "{:02d}:{:02d}:{:02d}.{:03d}".format(int(hours), int(minutes), int(seconds), int(milliseconds))


event_files = Path("/mnt/test/")
startlist_dir = "startlist/"

def get_white_list():
    print("Current whitelist")
    all_evnets = []

    with open("whitelist.txt","r") as outfile:
        data = json.load(outfile)

    all_evnets.extend(data["normal_whitelist"])
    all_evnets.extend( data["single_whitelist"])
    all_evnets.extend(data["stige_whitelist"])

    return data["stige_whitelist"], data["normal_whitelist"], data["single_whitelist"], all_evnets


def get_event():
    db_path = event_files / "Online.scdb"
    event_values = []
    try:
        with sqlite3.connect(str(db_path), isolation_level='EXCLUSIVE') as con:
            cur = con.cursor()
            cur.execute('SELECT C_VALUE FROM TPARAMETERS WHERE C_PARAM IN ("EVENT", "HEAT");')
            event_values = [row[0] for row in cur.fetchall()]
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
        with sqlite3.connect(str(db_path), isolation_level='EXCLUSIVE') as con:
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
    print("asd")
    db_path = event_files / eventfile
    startlist = []
    finish_times = {}
    with sqlite3.connect(str(db_path), isolation_level='EXCLUSIVE') as con:
        cur = con.cursor()
        print(mode)
        if mode == "FINALE" or "FINALE_SINGLE":
            query_startlist = f"SELECT C_NUM FROM TSTARTLIST_HEAT{heat};"
            query_timedata = f"SELECT C_NUM, C_TIME, C_STATUS, C_SPEED1 FROM TTIMEINFOS_HEAT{heat};"
            query_baseline_data = f"SELECT C_NUM, C_HOUR2 FROM TTIMERECORDS_HEAT{heat}_START;"
            try:
                cur.execute(query_baseline_data)
                test = [row for row in cur.fetchall()]
            
                data_dict = {}
            
                for row in test:
                    key = row[0]
                    value = int(row[1])
                    if key not in data_dict or value > data_dict[key]:
                        data_dict[key] = value
                
                baseline_time = dict(sorted(data_dict.items()))

            except:
                baseline_time = {}
        else:
            query_startlist = f"SELECT C_NUM FROM TSTARTLIST_PARQ2_HEAT{heat};"
            query_timedata = f"SELECT C_NUM, C_TIME, C_STATUS, C_SPEED1 FROM TTIMEINFOS_HEAT{heat};"

        cur.execute(query_startlist)
        startlist = [row for row in cur.fetchall()]
        
        cur.execute(query_timedata)
        finish_times = {row[0]: [row[1], row[2], row[3]] for row in cur.fetchall()}
        cur.close()
        print(startlist)

#    paired_startlist = [(x[0], y[0]) for x, y in zip(startlist[::2], startlist[1::2])]
#    if len(startlist) % 2: 
#        paired_startlist.append((startlist[-1][0],))  

    return startlist, finish_times, baseline_time

def index_event(events, index, event_order, current_event, finale=False):
    pass


def index_heat(events, pro, rookie):
    res_list = {}
    event_heats_dict = {}


    for a in events:
        match = re.search(r'Run (\d+)', a)
        if "Fellesstart Pro Kvalifisering" in a:
            match = re.search(r'Run (\d+)', a)
            if int(match[1]) <= pro["H1"]:
                name = str(a).replace(match[0],"") + "Heat 1"
                if name in res_list:   
                    res_list[name].append(events[a])
                else:
                    res_list[name]=[events[a]]
            elif int(match[1]) <= pro["H2"]:
                name = str(a).replace(match[0],"") + "Heat 2"
                if name in res_list:   
                    res_list[name].append(events[a])
                else:
                    res_list[name]=[events[a]]                
            elif int(match[1]) <= pro["H3"]:
                name = str(a).replace(match[0],"") + "Heat 3"
                if name in res_list:   
                    res_list[name].append(events[a])
                else:
                    res_list[name]=[events[a]]

        elif "Fellesstart Rookie Kvalifisering" in a:
            match = re.search(r'Run (\d+)', a)
            if int(match[1]) <= rookie["H1"]:
                name = str(a).replace(match[0],"") + "Heat 1"
                if name in res_list:   
                    res_list[name].append(events[a])
                else:
                    res_list[name]=[events[a]]
            elif int(match[1]) <= rookie["H2"]:
                name = str(a).replace(match[0],"") + "Heat 2"
                if name in res_list:   
                    res_list[name].append(events[a])
                else:
                    res_list[name]=[events[a]]                
            elif int(match[1]) <= rookie["H3"]:
                name = str(a).replace(match[0],"") + "Heat 3"
                if name in res_list:   
                    res_list[name].append(events[a])
                else:
                    res_list[name]=[events[a]]
        else:
            
            name = str(a).replace(match[0],"") + "Heat {0}".format(match[1])
            
            if name not in res_list:   
                res_list[name] = [events[a]]
    for a in res_list:
        event_heats_dict[a] = combine_entries(res_list[a])
    return event_heats_dict
    
def inject_string_to_dict(original_dict: dict, string_to_inject: str) -> dict:
    return {string_to_inject: original_dict}

def get_start_list_dict(startlist, competitors, time_data, mode, baseline_time):
    riders = {}
    newcount = 0

    # Define scores
    scores = {
        1: [9],
        2: [9, 6],
        3: [9, 6, 4],
        4: [9, 6, 4, 3]
    }

    for idx, pair in enumerate(startlist):
        if mode == "FINALE" or mode == "FINALE_SINGLE":
            for rider_num in [pair]:
                for comp in competitors:
                    for t in rider_num:
                        if time_data.get(t) is None:
                            time_data[t] = [0,0,0]
                        
                        if t == comp[0]:

                            if t in baseline_time and time_data[t][0] == 0:
                                newcount += 1
                                time_data[t].append(baseline_time[t])
                                riders[newcount] = (*comp, time_data[t], "Started")

                            elif t in time_data and t in baseline_time:
                                newcount += 1
                                time_data[t].append(baseline_time[t])
                                riders[newcount] = (*comp, time_data[t], "Done")

                            else:
                                newcount += 1
                                riders[newcount] = (*comp, [0,0,0,0], "Not_Started")

    # Sort riders by microseconds (ascending)
    sorted_riders = sorted(riders.items(), key=lambda item: item[1][5][0] if item[1][5][0] != 0 else float('inf'))
    

    # Assign points to riders
    #print(sorted_riders)
    if mode == "FINALE_SINGLE":
        pass
    else:
        for i, (key, value) in enumerate(sorted_riders):
            print(value)
            if value[5][0] > 0 and value[5][0] > 0:
                points = scores[len(sorted_riders)][i]
                print(points)
                riders[key][5].append(points)

            elif value[5][1] == 3 or value[5][1] == 2:
                points = 1
                riders[key][5].append(points)

            elif value[5][1] == 1:
                points = 0
                riders[key][5].append(points)

            elif value[5][0] == 0 and value[5][3] == 0:
                points = 0
                riders[key][5].append(points)

    return riders

def clean_event_data(data,filter="none"):
    new_dict={}
    for a in data:
        title_fixed = str(a).replace(" ","")
        try:
            int(filter[len(filter) - 1])
            if filter == title_fixed:
                new_dict[a]=data[a]
                return new_dict
        except:
            if filter in title_fixed:
                new_dict[a]=data[a]
            
    return new_dict

def get_all_events(empty = True):
    race_data = {}
    directory = 'startlist'
    event_names = api_get_event_name()
    for a in event_names:

        match = re.search(r'Event(\d+)Ex.scdb_(\d+)', a)
        heat = match.group(2)
        event_num = match.group(1)

        filename = ("Event{0}.scdb_{1}_.json".format(event_num, heat))

        with open(directory+"/"+filename, 'r') as file:
            file_content = file.read()
            json_content = json.loads(file_content)

            if empty == False:
                for b in json_content:
                    if json_content[b][5][0] != 0:
                        race_data[event_names[a]] = json_content
                        break
            else:
                race_data[event_names[a]] = json_content

    return race_data

def api_get_data(param, current_event="none"):
    race_data = {}
    directory = 'startlist'

    if param == "all":
        
        race_data = get_all_events()

    elif param == "current":
       
        with open('startlist/current.json', "r") as json_file:
            current = json.load(json_file)

        eventex = current[1]
        event = current[0]
        heat = current[2]

        with open("startlist/" + eventex + "_" + str(heat) + "_title_.json", "r") as json_file:
            title = json_file.readline()
        with open('startlist/' + event + "_" + str(heat) + '_.json', "r") as json_file:
            file_update = json.load(json_file)
        
        race_data[title] = file_update
    
    elif param == "event_list":
        race_data = {}
        directory = 'startlist'

        if param == "all":
            
            event_names = api_get_event_name()
            
            for a in event_names:

                match = re.search(r'Event(\d+)Ex.scdb_(\d+)', a)
                heat = match.group(2)
                event_num = match.group(1)

                filename = ("Event{0}.scdb_{1}_.json".format(event_num, heat))

                with open(directory+"/"+filename, 'r') as file:
                    file_content = file.read()
                    json_content = json.loads(file_content)
                    race_data[event_names[a]] = json_content

    elif param == "current_event_points":

        event_names = api_get_event_name()

        for a in event_names:
            if current_event[0] == event_names[a][:-8]:
                
                match = re.search(r'Event(\d+)Ex.scdb_(\d+)', a)
                heat = match.group(2)
                event_num = match.group(1)
                
                filename = ("Event{0}.scdb_{1}_.json".format(event_num, heat))

                with open(directory+"/"+filename, 'r') as file:
                    file_content = file.read()
                    json_content = json.loads(file_content)
                    race_data[event_names[a]] = json_content
        
        return assigne_points(race_data)

    else:
        race_data = {}
    return race_data

def assigne_points(json_string):
    tmp_drivers = ["asd"]

    return json_string
    
def api_get_event_name():
    events = {}
    directory = 'startlist'
    for filename in os.listdir(directory):
        if filename.endswith('.json'):
            filepath = os.path.join(directory, filename)
            if "Ex" in filepath and "current" not in filepath:
                with open(filepath, 'r') as file:
                    file_content = file.read()
                    events[filename] = file_content
    return events
    

def inject_heat(data):
    new_dict = {}
    for key, value in data.items():
        if value.startswith('Fellesstart'):
            match = re.search(r'Run (\d+)', value)
            if match:
                num = int(match.group(1))
                if num < 4:
                    value = value + " | Heat 1"
                elif num < 8:
                    value = value + " | Heat 2"
        new_dict[key] = value
    return new_dict

def inject_event(data):
    new_dict = {}
    tp = {}
    for a in data:
        pass

    return new_dict

def combine_entries(list_data):
    combined = {}
    for heat in list_data:
        for driver_id, driver_data in heat.items():
            if driver_id not in combined:
                combined[driver_id] = driver_data
            else:
                # add the points together
                combined[driver_id][5] = [x + y for x, y in zip(combined[driver_id][5], driver_data[5])]
                
                # update the time if it's not 0 and it's lower than the existing time
                if driver_data[5][0] != 0 and (combined[driver_id][5][0] == 0 or driver_data[5][0] < combined[driver_id][5][0]):
                    combined[driver_id][5][0] = driver_data[5][0]
    return combined

def combine_entries_new(dictionary):
    combined_dict = {}

    for a in dictionary:
        print(a)
    
    return combined_dict
