
from flask import Blueprint, render_template, request
import sqlite3
from app.lib.db_func import reload_event as reload_event_func


vmix_bp = Blueprint('vmix', __name__)


@vmix_bp.route('/vmix/active_driver_stats', methods=['GET'])
def active_driver_stats():
    
    return render_template('vmix/active_driver_dash.html')
