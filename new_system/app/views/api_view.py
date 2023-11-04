from flask import Blueprint, render_template, request
import sqlite3
from app.lib.db_operation import reload_event as reload_event_func
from app.lib.db_operation import update_active_event_stats, get_active_startlist, get_active_startlist_w_timedate
from app import socketio
from app.lib.utils import intel_sort



api_bp = Blueprint('api', __name__)

@api_bp.route('/api/send_data')
def send_data_to_room(msg):
    room = request.args.get('room')

    socketio.emit('response', msg, room=room)
    return {"message": "Data sent to the room"}

@api_bp.route('/api/update_active_drivers', methods=['GET','POST'])
def update_active_drivers():
    from app.models import ActiveDrivers
    from app import db
    
    if request.method == 'POST':
        return request.json
    else:
        return "Method not allowed"

@api_bp.route('/api/active_event_update', methods=['GET'])
def active_event_update():
    
    update_active_event_stats()
    send_data_to_room(get_active_startlist())
    return "Updated"



@api_bp.route('/api/update_active_startlist', methods=['GET'])
def update_active_startlist():
    return "Method not allowed"

@api_bp.route('/api/get_current_startlist', methods=['GET'])
def get_current_startlist():

    return get_active_startlist()

@api_bp.route('/api/get_current_startlist_w_data', methods=['GET'])
def get_current_startlist_w_data():
    intel_sort()
    return get_active_startlist_w_timedate()

@api_bp.route('/api/<string:tab_name>', methods=['GET','POST'])
def api(tab_name):
    if tab_name == 'reload_event':
        return reload_event()
    else:
        return "Invalid tab", 404

    
def reload_event():
    data = request.json
    print(data)
    reload_event_func(data["file"], data["run"])
    return data

