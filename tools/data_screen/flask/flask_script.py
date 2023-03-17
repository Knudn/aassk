from flask import Flask, render_template,request
from get_active_event import get_event, get_start_list,get_driver_data,get_start_list_dict
import json
import sqlite3
import os

con = sqlite3.connect("../test.db", check_same_thread=False)
cur = con.cursor()



def update_loop_index_scoreboard():
    if os.path.isfile("startlist/loop_score.txt"):
        active_dirlist = {}
        event_whitelist = ["Event036","Event012","Event041"]

        dir_list = os.listdir("startlist")
        counto = 0

        for a in event_whitelist:
            if a+".scdb_1_.json" in dir_list:
                counto += 1
                active_dirlist[counto] = [a+".scdb_1_.json"]
                active_dirlist[counto].append(a+"Ex.scdb_1_title_.json")

            if os.path.isfile("startlist/"+a+".scdb_2_.json"):
                counto = counto + 1
                active_dirlist[counto] = [a+".scdb_2_.json"]
                active_dirlist[counto].append(a+"Ex.scdb_2_title_.json")

        with open("startlist/loop_score.txt","r") as score_loop:
            count = score_loop.readline()

        count = int(count) + 1
        len(active_dirlist)
        if count > (len(active_dirlist)):
            count = 1
        with open("startlist/loop_score.txt","w") as score_loop:
            score_loop.write(str(count))
        
        print(active_dirlist[count])
        return active_dirlist[count]
        
    else:
        with open("startlist/loop_score.txt","w") as score_loop:
            score_loop.write("0")
    


def get_event_data():

    eventfile, eventex, heat = get_event()
    event_heat = [eventfile, eventex, heat]
    # Save current event data to a file



        
    con_title, con_per = get_driver_data(eventfile, heat)
    
    print(con_title)

    if "STIGE" in con_title.upper():
        with open("startlist/current.json", "w") as outfile:
            json.dump([False, False, False], outfile)
        return False, False, False
    ##IF IT IS A SINGLE TRACK IT WILL APPLY THESE CONFIGURATIONS
    elif "SINGLE" in con_title.upper():
        mode = "SINGLE"
    else:
        mode = "PARALLEL"

    with open("startlist/current.json", "w") as outfile:
        json.dump(event_heat, outfile)

    startlist, time_data = get_start_list(eventex, heat,mode)
    
    start_list_dict = get_start_list_dict(startlist, con_per, time_data,mode)
    
    print(mode)

    # Save start list dictionary to a file
    with open("startlist/" + eventfile + "_" + heat + "_" + ".json", "w") as outfile:
        print(start_list_dict)
        json.dump(start_list_dict, outfile)

        
    # Save race results to a file
    with open("startlist/" + eventex + "_" + heat + "_res_.json", "w") as outfile:
        json.dump(time_data, outfile)
    
    # Save driver list to a file 
    with open("startlist/" + eventex + "_" + heat + "_title_.json", "w") as outfile:
        outfile.write(con_title)
        

    
        # Return the start list dictionary, driver list and eventex
        return start_list_dict, con_title, eventex
    
# Call the get_event_data function to fetch the event data and save it to files
start_list_dict, con_title, eventex = get_event_data()


app = Flask(__name__)

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
    event, title = update_loop_index_scoreboard()

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

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=4433)