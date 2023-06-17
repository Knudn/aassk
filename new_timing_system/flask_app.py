from flask import Flask, request, render_template
from datetime import datetime
import json
import get_active_event

app = Flask(__name__)

def get_time_stamp(id):

    now = datetime.now()
    time_str = now.strftime('%H:%M:%S')
    fractional_seconds = str(now.microsecond // 1000).zfill(3)
    timestamp = f"{time_str}'{fractional_seconds}\""


    data = "<BOX {1} {0} 23 01 2 1567>\n".format(timestamp, id)
    return data

def load_people():
    with open('people.json', 'r') as f:
        people = json.load(f)
        print(people)
    return people

@app.route('/', methods=['GET'])
def home():
    people = load_people()
    return render_template('index.html', people=people)

@app.route('/click', methods=['POST'])
def button_click():
    id = str(request.form.get("id")).zfill(6)
    with open('data', 'w') as f:
        f.write(get_time_stamp(id))
    return 'OK', 200

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=8080)
