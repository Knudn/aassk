from flask import Flask, render_template,request, session
from get_active_event import *
from api_functions import generate_json_ladder_current
import json
import sqlite3
import os
from flask_cors import CORS

con = sqlite3.connect("../active_data.sql", check_same_thread=False)
cur = con.cursor()

data = {}
app = Flask(__name__)
CORS(app)


#Getting the event whitelist
stige_whitelist, normal_whitelist, single_whitelist, all_whitelist = get_white_list()


test = ["1","2","3"]

    


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



@app.route("/banner_obs")
def banner_obs():
    delay = 3000
    return render_template('banner_obs.html', time_delay=delay)


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

@app.route("/startlist_obs")
def startlist_obs():
    active_drivers = []
    current = []

    with open('startlist/current.json', "r") as json_file:
        current = json.load(json_file)

    eventex = current[1]
    event = current[0]
    heat = current[2]

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
                    b[7] = round(int(b[5]) / 1000, 3)

            return render_template('template_current_startlist_2v2_obs.html', data=data, con_title=title, active_drivers=active_drivers)

        except Exception as e:
            print("Error occurred while rendering startlist:", e)
            return render_template('template_current_startlist_2v2_obs.html', data=data, con_title=title, active_drivers=active_drivers)
    else:
        data = {}
        title = ""
        active_drivers = []
        return render_template('template_current_startlist_2v2_obs.html', data=data, con_title=title, active_drivers=active_drivers)

@app.route("/startlist-loop")
def startlist_loop():
    con_title = "asd"
    active_drivers = []
    start_list = {}
    current = []
    tmp_driver = []

    if 'position' not in session:
        session['position'] = 1
    elif session['position'] >= len(normal_whitelist):
        session['position'] = 1
    else:
        session['position'] = (session['position'] + 1)
    

    event, title = loop_sites(normal_whitelist, session['position'])
    
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
    event, title = loop_sites(normal_whitelist, "loop-startlist-single.txt")
    
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


@app.route('/testing')
def hello():
    index = session.get('index', 0) # Get the current index from session, or 0 if it's not set
    next_item = test[index % len(test)] # Get the next item of the list using modulo operator
    session['index'] = index + 1 # Update the index in session
    return f'Next item: {next_item}'

@app.route('/scoreboard-loop')
def scoreboard_loop():
    tmp_driver = []

    index = session.get('index', 0)

    if 'position' not in session:
        session['position'] = 1
    elif session['position'] >= len(all_whitelist):
        session['position'] = 1
    else:
        session['position'] = (session['position'] + 1)

    event, title = loop_sites(all_whitelist,session['position'])

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
    
@app.route('/scoreboard-loop-obs')
def scoreboard_loop_obs():
    tmp_driver = []

    index = session.get('index', 0)

    if 'position' not in session:
        session['position'] = 1
    elif session['position'] >= len(all_whitelist):
        session['position'] = 1
    else:
        session['position'] = (session['position'] + 1)

    event, title = loop_sites(all_whitelist,session['position'])

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
        return render_template('template_scoreboard_loop_obs.html', con_title=title, data=fix_sorted_lst)
    
@app.route("/stige")
def stige():

    current = []

    with open('startlist/current.json', "r") as json_file:
        current = json.load(json_file)

    eventex = current[1]
    event = current[0]

    with open('startlist/' + event + '_1_.json', "r") as json_file:
        data = json.load(json_file)

    with open("startlist/" + eventex + "_1_title_.json", "r") as json_file:
        title = json_file.readline()

    title = title[:-7]
        
    final_json = generate_json_ladder_current()
    if len(data) == 1:
        variables = {'team_width': 400,'score_width': 45,'match_margin': 60,'round_margin': 32,'scale':2}
    elif len(data) == 2:
        variables = {'team_width': 400,'score_width': 45,'match_margin': 60,'round_margin': 100,'scale':1.5}
    elif len(data) == 4:
        variables = {'team_width': 400,'score_width': 45,'match_margin': 90,'round_margin': 60,'scale':1.5}
    elif len(data) == 8:
        variables = {'team_width': 400,'score_width': 45,'match_margin': 60,'round_margin': 32,'scale':1.0}
    elif len(data) == 16:
        variables = {'team_width': 400,'score_width': 45,'match_margin': 60,'round_margin': 32,'scale':1.0}
    else:
        variables = {'team_width': 400,'score_width': 45,'match_margin': 60,'round_margin': 32,'scale':1.0}
    return render_template('ladders/teams-8.html', data=final_json, con_title=title, **variables)

@app.route('/api-ladder/<int:data_id>')
def get_data(data_id):

    if data_id == 0:
        data = generate_json_ladder_current()
        response = app.response_class(
        response=json.dumps(data),
        status=200,
        mimetype='application/json'
    )

    if data_id == 1:

        with open('startlist/current.json', "r") as json_file:
            current = json.load(json_file)

        eventex = current[1]
        heat = current[2]

        with open("startlist/" + eventex + "_" + str(heat) + "_title_.json", "r") as json_file:
            title = json_file.readline()
            title = title[:-7]
            response = "{},{}".format(title,("Run "+str(heat)))

    return response

@app.route("/current_scoreboard_obs")
def current_scoreboard_obs():

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
                b[5] = round(int(b[5]) / 1000, 3)
                b[6] = str(b[6])
                tmp_driver.append(b)
        
        sorted_lst = sorted(tmp_driver, key=lambda x: float('inf') if x[5] == 0.0 else x[5])

        fix_sorted_lst = [x for x in sorted_lst if x[5] != '0.0'] + [x for x in sorted_lst if x[5] == '0.0']

        return render_template('template_scoreboard_obs.html', con_title=title, data=fix_sorted_lst)
    else:
        title="None"
        data = []
        fix_sorted_lst=data
        return render_template('template_scoreboard_empty.html', con_title=title, data=fix_sorted_lst)

@app.route("/stige_obs")
def stige_obs():
    current = []

    with open('startlist/current.json', "r") as json_file:
        current = json.load(json_file)

    eventex = current[1]
    event = current[0]

    with open('startlist/' + event + '_1_.json', "r") as json_file:
        data = json.load(json_file)

    with open("startlist/" + eventex + "_1_title_.json", "r") as json_file:
        title = json_file.readline()

    title = title[:-7]
        
    final_json = generate_json_ladder_current()
    if len(data) == 1:
        variables = {'team_width': 400,'score_width': 45,'match_margin': 60,'round_margin': 32,'scale':2.5,'padding_top':0}
    elif len(data) == 2:
        variables = {'team_width': 400,'score_width': 45,'match_margin': 60,'round_margin': 100,'scale':1.5,'padding_top':75}
    elif len(data) == 4:
        variables = {'team_width': 400,'score_width': 45,'match_margin': 90,'round_margin': 60,'scale':1.3,'padding_top':0}
    elif len(data) == 8:
        variables = {'team_width': 400,'score_width': 45,'match_margin': 60,'round_margin': 40,'scale':0.9,'padding_top':0}
    elif len(data) == 16:
        variables = {'team_width': 400,'score_width': 45,'match_margin': 60,'round_margin': 32,'scale':1.0,'padding_top':0}
    else:
        variables = {'team_width': 400,'score_width': 45,'match_margin': 60,'round_margin': 32,'scale':1.0,'padding_top':0}
    return render_template('ladders/teams-8_obs.html', data=final_json, con_title=title, **variables)

@app.route("/current_scoreboard_top")
def current_scoreboard_top():

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
                b[5] = round(int(b[5]) / 1000, 3)
                b[6] = str(b[6])
                tmp_driver.append(b)
        
        sorted_lst = sorted(tmp_driver, key=lambda x: float('inf') if x[5] == 0.0 else x[5])

        fix_sorted_lst = [x for x in sorted_lst if x[5] != '0.0'] + [x for x in sorted_lst if x[5] == '0.0']

        return render_template('template_scoreboard_top.html', con_title=title, data=fix_sorted_lst)
    else:
        title="None"
        data = []
        fix_sorted_lst=data
        return render_template('template_scoreboard_empty.html', con_title=title, data=fix_sorted_lst)

if __name__ == '__main__':
    app.secret_key = 'your_secret_key' # Set a secret key for session encryption
    app.run(debug=True, host="0.0.0.0", port=4433)
