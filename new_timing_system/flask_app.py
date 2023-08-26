from flask import Flask, request, render_template, Response, jsonify, session
from datetime import datetime
import json
from get_active_event import *
import time
import requests
from flask_cors import CORS
import subprocess
import re

event_order = [
        "Singelstart Rookie Kvalifisering - Run 1", 
        "Singelstart Pro Kvalifisering - Run 1", 
        "Singelstart Rookie Kvalifisering - Run 2", 
        "Singelstart Pro Kvalifisering - Run 2",
        "Singelstart Rookie Finale - Run 1",
        "Fellesstart Pro Kvalifisering - Run 1",
        "Fellesstart Pro Kvalifisering - Run 2",
        "Fellesstart Pro Kvalifisering - Run 3",
        "Fellesstart Pro Kvalifisering - Run 4",
        "Fellesstart Pro Kvalifisering - Run 5",
        "Fellesstart Pro Kvalifisering - Run 6",
        "Fellesstart Pro Finale - Run 2",
        "Fellesstart Pro Finale - Run 1",
        ]


command = ['bash', '-c', 'source ./set_env.sh && env']
proc = subprocess.Popen(command, stdout = subprocess.PIPE)

app = Flask(__name__)
CORS(app)

app.config['SECRET_KEY'] = 'super secret key'

felles_heat_rookie={"H1":1,"H2":2,"H3":3}
felles_heat_pro={"H1":3,"H2":6,"H3":9}




def get_event_data():

    eventfile, eventex, heat = get_event()
    event_heat = [eventfile, eventex, heat]
    # Save current event data to a file

    con_title, con_per, heats = get_driver_data(eventfile, heat)
    app.config["current_title"] = [con_title]
    mode_title = con_title.upper()
    print(mode_title)
    if "STIGE" in mode_title:
        mode = "STIGE"

    elif "SINGLE" in mode_title:
        mode = "FINALE"
        
    elif "SINGELSTART" in mode_title:
        mode = "FINALE_SINGLE"

    elif "FELLESSTART" in mode_title:
        mode = "FINALE"
    else:
        mode = "PARALLEL"

    with open("startlist/current.json", "w") as outfile:
        json.dump(event_heat, outfile)
    

    startlist, time_data, baseline_time = get_start_list(eventex, heat, mode, heats)

    start_list_dict = get_start_list_dict(startlist, con_per, time_data,mode, baseline_time)


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


def get_time_stamp(id):

    now = datetime.now()
    time_str = now.strftime('%H:%M:%S')
    fractional_seconds = str(now.microsecond // 1000).zfill(3)
    timestamp = f"{time_str}'{fractional_seconds}\""
    data = "<BOX {1} {0} 23 01 2 1567>\n".format(timestamp, id)
    return data

@app.route('/', methods=['GET'])
def home():
    get_event_data()
    with open('startlist/current.json', "r") as json_file:
        current = json.load(json_file)

    eventex = current[1]
    event = current[0]
    heat = current[2]
    
    with open('startlist/' + event + "_" + heat + '_.json', "r") as json_file:
        file_update = json.load(json_file)

    return render_template('index.html', drivers=file_update)

@app.route('/scoreboard')
def scoreboard():
    return render_template('scoreboard.html')

@app.route('/scoreboard_infoscreen')
def infoscreen():
    return render_template('scoreboard_infoscreen.html')

@app.route('/loop_scoreboard_vmix')
def loop_vmix_scoreboard():
    return render_template('loop_vmix.html')

@app.route('/current_event_vmix')
def current_event_vmix():
    return render_template('current_run_vmix.html')

@app.route('/resultat')
def test():
    events = []
    heats_unsorted = api_get_event_name()
    heats = sorted(heats_unsorted.items(), key=lambda x:x[1])
    for a in dict(heats).values():
        data = str(a).split("-")[0]
        if data not in events:
            events.append(data)
    heats_all = dict(heats)
    return render_template('test.html', heats=heats_all.values(),events=events)

@app.route('/startlist')
def startlist():
    return render_template('startliste.html')


@app.route('/event/<param>', methods=['GET'])
def event(param):
    if param == "test":
        tmp_list = []
        if 'index' in session:
            session['index'] += 1
        else:
            session['index'] = 1
        data = get_all_events(False)
        for a in data:
            for b in event_order:
                if str(a) == b:
                    title_name = str(a).split("-")[0][:-1]
                    if title_name not in tmp_list:
                        tmp_list.append(title_name)
        
        if session['index'] >= len(tmp_list):
            session['index'] = 0
        event_get = tmp_list[session['index']]
        drift = str(event_get).replace(" ","")
        resp = clean_event_data(data, drift)
        
        event = resp
        

    else:
        event = {}
        data = get_all_events()
        event = clean_event_data(data,param)
        for a in data:
            if str(a).replace(" ","") == param:
                event[a] = data[a]
                

    return event

@app.route('/random_heat')
def random_heat():
    if 'index' in session:
        session['index'] += 1
    else:
        session['index'] = 1
    
    events = get_all_events(False)
    index_heat_data = index_heat(events, felles_heat_pro, felles_heat_rookie)

    if session['index'] >= len(index_heat_data.keys()):
        session['index'] = 0
        
    keys = list(index_heat_data.keys())[session['index']]
    data = inject_string_to_dict(index_heat_data[keys], keys)
    return data

@app.route('/scoreboard_vmix')
def scoreboard_vmix():
    return render_template('scoreboard_vmix.html')

@app.route('/api/driver_status')
def driver_status():
    #get_event_data()
    data = {}
    with open('startlist/current.json', "r") as json_file:
        current = json.load(json_file)

    eventex = current[1]
    event = current[0]
    heat = current[2]
    tmp_driver = []
    
    with open('startlist/' + event + "_" + heat + '_.json', "r") as json_file:
            file_update = json.load(json_file)

    for a in file_update:

        time = round(int(file_update[a][5][0]) / 1000, 3)
        if file_update[a][5][0] != 0 and file_update[a][5][1] == 0 and file_update[a][5][2] == 0:
            data[file_update[a][0]] = {"color":"green", "time": str(time), "state":"Ferdig", "base_time":file_update[a][5][3]}
        elif file_update[a][5][1] == 3:
            data[file_update[a][0]] = {"color":"red", "time": 0, "state":"Diskvalifisert", "base_time":file_update[a][5][3]}
        elif file_update[a][5][1] == 2:
            data[file_update[a][0]] = {"color":"orange", "time": 0, "state":"Ikke Fullført", "base_time":file_update[a][5][3]}
        elif file_update[a][5][1] == 1:
            data[file_update[a][0]] = {"color":"red", "time": 0, "state":"Kunne ikke Starte", "base_time":file_update[a][5][3]}
        elif file_update[a][5][3] != 0 and file_update[a][5][0] == 0 and file_update[a][5][1] == 0 and file_update[a][5][2] == 0:
            data[file_update[a][0]] = {"color":"blue", "time": 0, "state":"Startet!", "base_time":file_update[a][5][3]}
        else:
            data[file_update[a][0]] = {"color":"gray", "time": 0, "state":"Ikke Startet", "base_time":file_update[a][5][3]}

    response = app.response_class(
        response=json.dumps(data),
        status=200,
        mimetype='application/json'
    )
    return response

@app.route('/update')
def driver_status_test():
    get_event_data()

    with open('startlist/current.json', "r") as json_file:
        current = json.load(json_file)

    eventex = current[1]
    heat = current[2]

    with open('startlist/' + eventex + "_" + heat + '_title_.json', "r") as title:
            title = title.readlines()

    app.config["current_title"] = title
    return {'status': 'success'}

@app.route('/api/driver_data/<param>', methods=['GET'])
def api_data(param):

    if param == "title":
        respone = app.config["current_title"]
    elif param == "title_obs":
        respone = app.config["current_title"][0]
        respone = str(respone).split("-")
    elif param == "current":
        data = get_all_events()
        dictlist = {}
        for a in data:
            if str(a) == app.config["current_title"][0]:
                dictlist[a] = data[a]
        return dictlist
    elif param == "current_event_points":
        title = [app.config["current_title"][0][:-8]]
        respone = api_get_data(param,title)
        
    elif param == "next_event":
        current_event = app.config["current_title"][0]
        current_event = (event_order.index(current_event) + 1)
        data = get_all_events()
        formated_event = str(event_order[current_event]).replace(" ","")
        next_event = clean_event_data(data, formated_event)
        
        return next_event 
    elif param == "nextnext":
        current_event = app.config["current_title"][0]
        current_event = (event_order.index(current_event) + 2)
        data = get_all_events()
        formated_event = str(event_order[current_event]).replace(" ","")
        next_event = clean_event_data(data, formated_event)

        return next_event
    elif param == "all_startlist":
        data = get_all_events()
        array_tmp = []
        for a in event_order:
            for b in data:
                if a == str(b):
                    array_tmp.append((a, data[b]))
        for a in array_tmp:
            print(a)
        return jsonify(array_tmp)
    return respone           

@app.route('/api/submit_timestamp',methods=['POST'])
def manual_timestamp():
    timestamp = str(request.form.get("timestamp"))
    id = str(request.form.get("id"))
    start_list_dict, con_title, eventex = get_event_data()

    for a in start_list_dict:
        if start_list_dict[a][0] == int(id):
            basetime_stamp = start_list_dict[a][5][3]
    print(timestamp, basetime_stamp)
    if int(timestamp) > basetime_stamp:
        basetime_stamp_final = (int(timestamp) + (basetime_stamp))
    else:
        basetime_stamp_final = ((basetime_stamp) + int(timestamp))
    print(basetime_stamp_final)
   
    print(convert_microseconds_to_time((basetime_stamp - 1) - int(timestamp)))
    time_stamp_new = convert_microseconds_to_time(basetime_stamp_final)
    print(time_stamp_new)

    data = "<BOX {1} {0} 23 01 2 1567>\n".format(time_stamp_new, id.zfill(6))
    data += "\n"
    response = requests.post('http://192.168.1.50:7777', data={'message': data})
    start_list_dict, con_title, eventex = get_event_data()
    time.sleep(1)
    return {'status': 'success'}

@app.route('/api/button_click', methods=['POST'])
def button_click():
    
    driver_id = str(request.form.get("id")).zfill(6)
    
    with open('data', 'w') as f:
        f.write(get_time_stamp(driver_id))

    get_event_data()
    return {'status': 'success'}

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=8080)
