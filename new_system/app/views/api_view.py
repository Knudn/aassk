
from flask import Blueprint, render_template, request
import sqlite3
from app.lib.db_func import reload_event as reload_event_func


api_bp = Blueprint('api', __name__)


@api_bp.route('/api/<string:tab_name>', methods=['GET','POST'])
def api(tab_name):
    if tab_name == 'reload_event':
        return reload_event()
    else:
        return "Invalid tab", 404
    
def reload_event():
    data = request.json
    reload_event_func(data["file"], data["run"])
    return data