from flask import Flask, render_template,request
from get_active_event import get_event, get_start_list,get_driver_data,get_start_list_dict
import json
import sqlite3
con = sqlite3.connect("../test.db", check_same_thread=False)
cur = con.cursor()




def get_event_data():

    eventfile, eventex = get_event()
    con_title, con_per = get_driver_data(eventfile)
    startlist, time_data = get_start_list(eventex)
    print(time_data)
    start_list_dict = get_start_list_dict(startlist, con_per, time_data)

    #startlist_json = json.dumps(start_list_dict, indent = 4) 
    with open("startlist/" + eventfile+".json", "w") as outfile:

        json.dump(start_list_dict, outfile)

    with open("startlist/" + eventex+"_res_.json", "w") as outfile:
        json.dump(time_data, outfile)
    
    with open("startlist/" + eventex+ "_title_.json", "w") as outfile:
        json.dump(con_title, outfile)

    with open("startlist/current.json", "w") as outfile:
        outfile.write(eventfile)

    return start_list_dict, con_title, eventex


start_list_dict, con_title, eventex = get_event_data()
app = Flask(__name__)

@app.route("/startlist")
def startlist():
    con_title = "asd"
    active_drivers = []
    start_list = {}

    with open('startlist/current.json', "r") as current_event:
        current = current_event.read()

    with open('startlist/' + current + '.json') as json_file:
        data = json.load(json_file)

    with open("startlist/" + eventex+ "_title_.json") as json_file:
        title = json_file.readline()

    with open("startlist/" + eventex+"_res_.json") as json_file:
        race_res = json.load(json_file)
    
    for row in cur.execute("SELECT c_num FROM active_drivers"):
        for b in row:
            active_drivers.append(int(b))

    return render_template('template_current_startlist.html', data=data, con_title=con_title, active_drivers=active_drivers, )

@app.route("/current_scoreboard")
def current_scoreboard():
    con_title = "asd"

    tmp_driver = []
    with open('startlist/current.json', "r") as current_event:
        current = current_event.read()

    with open('startlist/' + current + '.json') as json_file:
        data = json.load(json_file)

    with open('startlist/current.json', "r") as current_event:
        current = current_event.read()
    
    for a in data:
        for b in data[a]:
            #b[5] = str(seconds) + "." + str(milliseconds)
            b[5] = round(int(b[5]) / 1000, 3)
            tmp_driver.append(b)

    sorted_lst = sorted(tmp_driver, key=lambda x: float('inf') if x[5] == 0.0 else x[5])

    fix_sorted_lst = [x for x in sorted_lst if x[5] != '0.0'] + [x for x in sorted_lst if x[5] == '0.0']
    #reversed_lst = sorted_lst[::-1]


    return render_template('template_scoreboard.html', con_title=con_title, data=fix_sorted_lst)


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

    # Code to fetch the updated data

    with open('startlist/' + current + '.json') as json_file:
        data = json.load(json_file)

    with open("startlist/" + eventex+"_res_.json") as json_file:
        race_res = json.load(json_file)

    # Return the updated data in JSON format
    return jsonify(data=data, race_res=race_res)

@app.route('/scoreboard-loop')
def scoreboard_loop():
    
    # Code to fetch the updated data

    with open('startlist/' + current + '.json') as json_file:
        data = json.load(json_file)

    with open("startlist/" + eventex+"_res_.json") as json_file:
        race_res = json.load(json_file)

    # Return the updated data in JSON format
    return jsonify(data=data, race_res=race_res)


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=4433)