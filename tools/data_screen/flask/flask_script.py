from flask import Flask, render_template
from get_active_event import get_event, get_start_list,get_driver_data,get_start_list_dict
import json

def get_event_data():

    eventfile, eventex = get_event()
    con_title, con_per = get_driver_data(eventfile)
    startlist, time_data = get_start_list(eventex)
    start_list_dict = get_start_list_dict(startlist,con_per)
#    startlist_json = json.dumps(start_list_dict, indent = 4) 

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
    with open('startlist/current.json', "r") as current_event:
        current = current_event.read()

    with open('startlist/' + current + '.json') as json_file:
        data = json.load(json_file)

    with open("startlist/" + eventex+ "_title_.json") as json_file:
        title = json_file.readline()

    with open("startlist/" + eventex+"_res_.json") as json_file:
        race_res = json.load(json_file)

    print(race_res, data)
    return render_template('template_current_startlist.html', data=data, con_title=con_title, )

@app.route("/new_event")
def new_event():
    get_event_data()

    return "Updated event"

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=4433)