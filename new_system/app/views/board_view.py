from app import socketio
from flask import Blueprint, render_template, request
from app.lib.db_operation import reload_event as reload_event_func
from flask_socketio import join_room, send
from app.models import SpeakerPageSettings
from app import db

board_bp = Blueprint('board', __name__)

@board_bp.route('/board/test')
def board():
    return render_template('board/test.html')

@board_bp.route('/board/scoreboard')
def scoreboard():
    return render_template('board/scoreboard.html')

@board_bp.route('/board/speaker', methods = ['GET', 'POST'])
def speaker():
    SpeakerPageConfig = SpeakerPageSettings.query.first()

    if request.method == 'POST':
        data = request.get_json()

        SpeakerPageConfig.match_parrallel = data["matchingParallel"]
        SpeakerPageConfig.h_server_url = data["h_server_url"]

        db.session.commit()
        print(request.get_json())
    
    SpeakerPageConfig_json = {"matching_parallel":SpeakerPageConfig.match_parrallel,"h_server_url":SpeakerPageConfig.h_server_url}

    return render_template('board/speaker_board.html', SpeakerPageConfig_json=SpeakerPageConfig_json)
