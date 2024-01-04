from app import socketio
from flask import Blueprint, render_template, request, session
from app.lib.db_operation import reload_event as reload_event_func
from flask_socketio import join_room, send
from app.models import SpeakerPageSettings
from app import db
from sqlalchemy import func


board_bp = Blueprint('board', __name__)

@board_bp.route('/board/test')
def board():
    return render_template('board/test.html')

@board_bp.route('/board/scoreboard')
def scoreboard():
    return render_template('board/scoreboard.html')

@board_bp.route('/board/ladder/')
def ladders():
    ladder = request.args.get('ladder', default='', type=str)
    print(ladder)
    if ladder == '':
        return render_template('board/ladder/active_ladder.html')
    else:
        return render_template('board/ladder/teams-{0}.html'.format(ladder))

@board_bp.route('/board/ladder/loop')
def ladders_loop():
    return render_template('board/ladder/ladder_loop.html')

@board_bp.route('/board/scoreboard_loop')
def scoreboard_loop():

    from app.models import Session_Race_Records, ActiveEvents
    import random

    session['index'] = session.get('index', 0) + 1

    query = db.session.query(
            Session_Race_Records.id,
            Session_Race_Records.first_name,
            Session_Race_Records.last_name,
            Session_Race_Records.title_1,
            Session_Race_Records.title_2,
            Session_Race_Records.heat,
            Session_Race_Records.finishtime,
            Session_Race_Records.snowmobile,
            Session_Race_Records.penalty
        ).filter(
            (Session_Race_Records.title_1 + Session_Race_Records.title_2).like('%Parallel%')
        ).filter(
            Session_Race_Records.finishtime != 0
        ).group_by(
            Session_Race_Records.title_1, Session_Race_Records.title_2
        ).having(
            Session_Race_Records.heat == func.max(Session_Race_Records.heat)
        )

    # Execute the query to get the results
    results = query.all()
    max_len = len(results)
    event_int = random.randint(0, max_len-1)

    title_combo = results[event_int][3] + " " + results[event_int][4]

    query = db.session.query(ActiveEvents.event_file).filter(
        ActiveEvents.event_name == title_combo
    )

    results = query.first()
    
    return str(session['index'])

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
