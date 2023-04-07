from flask import Flask, render_template_string, session
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)

my_list = ["item1", "item2", "item3", "item4", "item5"]

def iter_list():
    if 'position' not in session:
        session['position'] = 0
    else:
        session['position'] = (session['position'] + 1) % len(my_list)
    return my_list[session['position']]

@app.route("/")
def index():
    next_item = iter_list()
    return render_template_string('''<html>
<head>
  <title>Iterating List</title>
</head>
<body>
  <h1>Current item: {{ item }}</h1>
  <p><a href="/">Refresh</a> to get the next item.</p>
</body>
</html>''', item=next_item)

if __name__ == '__main__':
    app.secret_key = 'your_secret_key' # Set a secret key for session encryption
    app.run(debug=True, host="0.0.0.0", port=4433)
