from flask import Flask, render_template,request
from get_active_event import *
from api_functions import generate_json_ladder_current, generate_json_ladder_current_new
import json
import sqlite3
import os
from flask_cors import CORS

con = sqlite3.connect("../active_data.sql", check_same_thread=False)
cur = con.cursor()

data = {}

#Getting the event whitelist
stige_whitelist, normal_whitelist, single_whitelist = get_white_list()


def update_loop_index_scoreboard(whitelist, cache_name):
    if os.path.isfile("startlist/"+cache_name):
        active_dirlist = {}

        dir_list = os.listdir("startlist")
        counto = 0

        for a in whitelist:
            if a+".scdb_1_.json" in dir_list:

                counto += 1
                active_dirlist[counto] = [a+".scdb_1_.json"]
                active_dirlist[counto].append(a+"Ex.scdb_1_title_.json")

            if os.path.isfile("startlist/"+a+".scdb_2_.json"):
                counto = counto + 1
                active_dirlist[counto] = [a+".scdb_2_.json"]
                active_dirlist[counto].append(a+"Ex.scdb_2_title_.json")

        with open("startlist/"+cache_name,"r") as score_loop:
            count = score_loop.readline()

        count = int(count) + 1
        len(active_dirlist)
        if count > (len(active_dirlist)):
            count = 1
        with open("startlist/"+cache_name,"w") as score_loop:
            score_loop.write(str(count))
        

        return active_dirlist[count]
        
    else:
        with open("startlist/"+cache_name,"w") as score_loop:
            score_loop.write("0")
    


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
CORS(app)

@app.route("/startlist")
def startlist():
    con_title = "asd"
    active_drivers = []
    start_list = {}
    current = []

    with open('startlist/current.json', "r") as json_file:
        current = json.load(json_file)

    eventex = current[1]
    event = current[0]
    heat = current[2]
    tmp_driver = []

    if eventex != False or heat != False or event != False:

        try:

            # Load the start list dictionary from the file
            with open('startlist/' + current[0] + "_" + current[2] + '_.json',"r") as json_file:
                data = json.load(json_file)
            
            # Load the driver list from the file
            with open("startlist/" + eventex + "_" + current[2] + "_title_.json", "r") as json_file:
                title = json_file.readline()
            
            # Load the active drivers from the database
            for row in cur.execute("SELECT c_num FROM active_drivers"):
                for b in row:
                    active_drivers.append(int(b))
            for a in data:
                for b in data[a]:
                   # b[6] = str(b[6])
                    #b[5] = str(seconds) + "." + str(milliseconds)
                    b[7] = round(int(b[5]) / 1000, 3)


            # Render the start list template with the loaded data

            return render_template('template_current_startlist_2v2.html', data=data, con_title=title, active_drivers=active_drivers)

        except Exception as e:
            print("Error occurred while rendering startlist:", e)
            return render_template('template_current_startlist_2v2.html', data=data, con_title=title, active_drivers=active_drivers)
    else:
        data = {}
        title = ""
        active_drivers = []
        return render_template('template_current_startlist_2v2.html', data=data, con_title=title, active_drivers=active_drivers)

@app.route("/startlist-loop")
def startlist_loop():
    con_title = "asd"
    active_drivers = []
    start_list = {}
    current = []
# Load the active drivers from the database

    tmp_driver = []
    event, title = update_loop_index_scoreboard(normal_whitelist, "loop-normal.txt")
    
    with open('startlist/'+event, "r") as json_file:
        data = json.load(json_file)
    with open("startlist/"+title, "r") as json_file:
        title = json_file.readline()

    for a in data:
        for b in data[a]:
            #b[5] = str(seconds) + "." + str(milliseconds)
            b[7] = round(int(b[5]) / 1000, 3)
            
    for a in data:
        for b in data[a]:
            #b[5] = str(seconds) + "." + str(milliseconds)
            b[5] = round(int(b[5]) / 1000, 3)
            b[6] = str(b[6])
            tmp_driver.append(b)

    return render_template('template_current_startlist_2v2_loop.html', data=data, con_title=title)
    
@app.route("/startlist-single-loop")
def startlist_single_loop():
    con_title = "asd"
    active_drivers = []
    start_list = {}
    current = []
# Load the active drivers from the database

    tmp_driver = []
    event, title = update_loop_index_scoreboard(normal_whitelist, "loop-startlist-single.txt")
    
    with open('startlist/'+event, "r") as json_file:
        data = json.load(json_file)
    with open("startlist/"+title, "r") as json_file:
        title = json_file.readline()

    for a in data:
        for b in data[a]:
            #b[5] = str(seconds) + "." + str(milliseconds)
            b[7] = round(int(b[5]) / 1000, 3)
            
    for a in data:
        for b in data[a]:
            #b[5] = str(seconds) + "." + str(milliseconds)
            b[5] = round(int(b[5]) / 1000, 3)
            b[6] = str(b[6])
            tmp_driver.append(b)

    return render_template('template_current_startlist_1v1.html', data=data, con_title=title)

@app.route("/startlist-single")
def startlist_single():
    con_title = "asd"
    active_drivers = []
    start_list = {}
    current = []
    with open('startlist/current.json', "r") as json_file:
        current = json.load(json_file)
    eventex = current[1]
    event = current[0]
    heat = current[2]
    tmp_driver = []

    if eventex != False or heat != False or event != False:

        try:

            # Load the start list dictionary from the file
            with open('startlist/' + current[0] + "_" + current[2] + '_.json',"r") as json_file:
                data = json.load(json_file)
            
            # Load the driver list from the file
            with open("startlist/" + eventex + "_" + current[2] + "_title_.json", "r") as json_file:
                title = json_file.readline()
            
            # Load the active drivers from the database
            for row in cur.execute("SELECT c_num FROM active_drivers"):
                for b in row:
                    active_drivers.append(int(b))
            for a in data:
                for b in data[a]:
                    #b[5] = str(seconds) + "." + str(milliseconds)
                    b[7] = round(int(b[5]) / 1000, 3)
            # Render the start list template with the loaded data
            return render_template('template_current_startlist_1v1.html', data=data, con_title=title, active_drivers=active_drivers)
        
        except Exception as e:
            print("Error occurred while rendering startlist:", e)
            return render_template('template_current_startlist_1v1.html', data=data, con_title=title, active_drivers=active_drivers)
    else:
        data = {}
        title = ""
        active_drivers = []
        return render_template('template_current_startlist_1v1.html', data=data, con_title=title, active_drivers=active_drivers)



@app.route("/current_scoreboard")
def current_scoreboard():

    with open('startlist/current.json', "r") as json_file:
        current = json.load(json_file)

    eventex = current[1]
    event = current[0]
    heat = current[2]
    tmp_driver = []

    if eventex != False or heat != False or event != False:

        with open('startlist/' + event + "_" + str(heat) + '_.json', "r") as json_file:
            data = json.load(json_file)

        with open("startlist/" + eventex + "_" + str(heat) + "_title_.json", "r") as json_file:
            
            title = json_file.readline()
        
        for a in data:
            for b in data[a]:
                #b[5] = str(seconds) + "." + str(milliseconds)
                b[5] = round(int(b[5]) / 1000, 3)
                b[6] = str(b[6])
                tmp_driver.append(b)
        
        sorted_lst = sorted(tmp_driver, key=lambda x: float('inf') if x[5] == 0.0 else x[5])

        fix_sorted_lst = [x for x in sorted_lst if x[5] != '0.0'] + [x for x in sorted_lst if x[5] == '0.0']
        #reversed_lst = sorted_lst[::-1]


        return render_template('template_scoreboard.html', con_title=title, data=fix_sorted_lst)
    else:
        title="None"
        data = []
        fix_sorted_lst=data
        return render_template('template_scoreboard_empty.html', con_title=title, data=fix_sorted_lst)

@app.route("/new_event")
def new_event():
    get_event_data()
    return "Updated event"

@app.route("/active_drivers", methods=['POST'])
def active_drivers():
    drivers = []
    bid = request.form['bid']
    players = json.loads(bid)
    
    with open("startlist/active_drivers.json", "w") as outfile:
        json.dump(players, outfile)
        return "Updated active drivers"

@app.route('/update-data-startlist')
def update_data():


    return render_template('template_scoreboard_obs.html')

@app.route('/scoreboard-loop')
def scoreboard_loop():

    tmp_driver = []
    event, title = update_loop_index_scoreboard(all_evnets,"loop-scoreb.txt")

    with open('startlist/'+event, "r") as json_file:
        data = json.load(json_file)
    with open("startlist/"+title, "r") as json_file:
        title = json_file.readline()
        
        for a in data:
            for b in data[a]:
                #b[5] = str(seconds) + "." + str(milliseconds)
                b[5] = round(int(b[5]) / 1000, 3)
                b[6] = str(b[6])
                tmp_driver.append(b)
        
        sorted_lst = sorted(tmp_driver, key=lambda x: float('inf') if x[5] == 0.0 else x[5])
        fix_sorted_lst = [x for x in sorted_lst if x[5] != '0.0'] + [x for x in sorted_lst if x[5] == '0.0']
        #reversed_lst = sorted_lst[::-1]
        return render_template('template_scoreboard_loop.html', con_title=title, data=fix_sorted_lst)


@app.route("/stige")
def stige():
    con_title = "asd"
    active_drivers = []
    start_list = {}
    current = []

    with open('startlist/current.json', "r") as json_file:
        current = json.load(json_file)
        
    final_json = generate_json_ladder_current(current)

    return render_template('ladders/teams-8.html', data=final_json)

@app.route('/api-ladder/<int:data_id>')
def get_data(data_id):

    if data_id == 0:
        active_drivers = []
        for row in cur.execute("SELECT c_num FROM active_drivers"):
            for b in row:
                active_drivers.append(int(b))
        data = generate_json_ladder_current(active_drivers)

    elif data_id == 2:
        active_drivers = []
        for row in cur.execute("SELECT c_num FROM active_drivers"):
            for b in row:
                active_drivers.append(int(b))
        data = generate_json_ladder_current_new(active_drivers)
    elif data_id == 4:
        data = {"id": 4, "name": "Data 2", "value": 20}
    elif data_id == 8:
        data = {"id": 4, "name": "Data 2", "value": 20}
    else:
        data = {"error": "Data not found"}
    
    response = app.response_class(
        response=json.dumps(data),
        status=200,
        mimetype='application/json'
    )

    return response

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=4433)
