from app import socketio
from flask import Blueprint, render_template, request
from app.lib.db_operation import reload_event as reload_event_func
from flask_socketio import join_room, send

board_bp = Blueprint('board', __name__)

@board_bp.route('/board/test')
def board():
    return render_template('board/test.html')

@board_bp.route('/board/scoreboard')
def scoreboard():
    return render_template('board/scoreboard.html')
