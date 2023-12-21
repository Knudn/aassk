from flask import Blueprint, request, send_from_directory, session
import sqlite3
from app.lib.db_operation import reload_event as reload_event_func
from app.lib.db_operation import update_active_event_stats, get_active_startlist, get_active_startlist_w_timedate, get_specific_event_data
from app import socketio
from app.lib.utils import intel_sort, update_info_screen, export_events
from sqlalchemy import func



api_bp = Blueprint('api', __name__)

@api_bp.route('/api/init', methods=['POST'])
def receive_init():
    from app.models import InfoScreenInitMessage
    from app import db
    import hashlib

    data = request.json
    hostname = data.get('Hostname')
    ip = request.remote_addr
    id_hash = hashlib.md5((str(ip)+str(hostname)).encode()).hexdigest()[-5:]

    existing_message = InfoScreenInitMessage.query.filter_by(unique_id=id_hash).first()

    if existing_message:
        return {"Added":id_hash, "Approved": existing_message.approved}
    else:
        new_message = InfoScreenInitMessage(hostname=hostname, ip=ip, unique_id=id_hash)
        db.session.add(new_message)
        db.session.commit()

        return {"Added":id_hash, "Approved": False}

        
@api_bp.route('/api/infoscreen_asset/<filename>')
def infoscreen_asset(filename):
    return send_from_directory('static/assets/infoscreen', filename)

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

@api_bp.route('/api/export', methods=['GET'])
def export():
    events = request.args.get('events', default=None)
    if events == 'all':
        
        return export_events()
    elif events == 'active':
        return get_active_startlist_w_timedate()
    else:
        return 'No events parameter provided'

@api_bp.route('/api/get_current_startlist', methods=['GET'])
def get_current_startlist():

    return get_active_startlist()

@api_bp.route('/api/get_current_startlist_w_data', methods=['GET'])
def get_current_startlist_w_data():
    
    return get_active_startlist_w_timedate()

@api_bp.route('/api/get_specific_event_data', methods=['GET'])
def get_specific_event_data_view():

    from app.models import Session_Race_Records, ActiveEvents
    import random
    from app import db
    
    event_filter = request.args.get('event_filter', default='', type=str)
    heat_insert = request.args.get('heat', default='', type=str)

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
        (Session_Race_Records.title_1 + Session_Race_Records.title_2).like(f'%{event_filter}%')
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
    if max_len == 0:
        return "None"
    event_int = random.randint(0, max_len-1)
    heat = []

    title_combo = results[event_int][3] + " " + results[event_int][4]

    query = db.session.query(ActiveEvents.event_file, ActiveEvents.run).filter(
        ActiveEvents.event_name == title_combo
    )

    results = query.all()
    if heat_insert == '':
        for a in results:
            heat.append(a[1])
    elif heat_insert == "latest":
        for a in results:
            heat.append(a[1])
        print(max(heat))
    else:
        heat.append(heat_insert)




    event = [{'db_file':results[0][0], "SPESIFIC_HEAT":heat}]
    return {"Timedata":get_specific_event_data(event_filter=event),"event_data":[title_combo]}

@api_bp.route('/api/get_event_order', methods=['GET'])
def get_event_order():
    from app.models import ActiveEvents
    from app.lib.db_operation import get_active_event
    event_order = ActiveEvents.query.order_by(ActiveEvents.sort_order).all()
    current_active_event = get_active_event()[0]

    data = []
    
    for a in event_order:

        if str(a.event_file) == str(current_active_event["db_file"]) and str(current_active_event["SPESIFIC_HEAT"]) == str(a.run):
            state = True
        else:
            state = False
        data.append({"Order":a.sort_order, "Event":a.event_name, "Enabled":a.enabled, "Heat":a.run, "Active":state})

    
    return data

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

@api_bp.route('/api/get_timedata/', methods=['GET'])
def get_timedata():
    from app.models import Session_Race_Records
    from flask import request
    from sqlalchemy import desc

    def format_db_rsp(a):
        return {
            "first_name": a.first_name,
            "last_name": a.last_name,
            "title_1": a.title_1,
            "title_2": a.title_2,
            "heat": a.heat,
            "finishtime": a.finishtime,
            "snowmobile": a.snowmobile,
            "penalty": a.penalty
        }

    events = request.args.get('events', default='False', type=str)
    heat = request.args.get('heat', default=None, type=str)
    title_1 = request.args.get('title_1', default=None, type=str)
    title_2 = request.args.get('title_2', default=None, type=str)
    single_all = request.args.get('single_all', default='false', type=str)
    entries_per_filter = request.args.get('entries_per_filter', default=1, type=int)
    unique_names = request.args.get('unique_names', default='false', type=str).lower() == 'true'
    ignore_penalty = request.args.get('ignore_penalty', default='false', type=str).lower() == 'true'

    if heat and heat.isdigit():
        heat = int(heat)

    event_data = {}

    if single_all != 'false':
        filter_combinations = [
            ('title_1', title_1),
            ('title_2', title_2),
            ('heat', heat),
            ('title_1+title_2', (title_1, title_2)),
            ('title_1+title_2+heat', (title_1, title_2, heat))
        ]

        for combo_name, filters in filter_combinations:
            query = Session_Race_Records.query

            if isinstance(filters, tuple):
                if 'title_1' in combo_name and title_1:
                    query = query.filter(Session_Race_Records.title_1 == title_1)
                if 'title_2' in combo_name and title_2:
                    query = query.filter(Session_Race_Records.title_2 == title_2)
                if 'heat' in combo_name and heat:
                    query = query.filter(Session_Race_Records.heat == heat)
            else:
                if combo_name == 'title_1' and title_1:
                    query = query.filter(Session_Race_Records.title_1 == title_1)
                elif combo_name == 'title_2' and title_2:
                    query = query.filter(Session_Race_Records.title_2 == title_2)
                elif combo_name == 'heat' and heat:
                    query = query.filter(Session_Race_Records.heat == heat)

            query = query.filter(Session_Race_Records.finishtime != 0)
            query = query.filter(Session_Race_Records.penalty == 0)

            if unique_names:
                # Subquery for unique driver names with min finishtime within each filter
                subquery = query.with_entities(
                    Session_Race_Records.first_name,
                    Session_Race_Records.last_name,
                    func.min(Session_Race_Records.finishtime).label('min_finishtime')
                ).group_by(
                    Session_Race_Records.first_name, 
                    Session_Race_Records.last_name
                ).subquery()  # Create a subquery object

                # Main query joins with the subquery
                query = Session_Race_Records.query.join(
                    subquery,
                    (Session_Race_Records.first_name == subquery.c.first_name) &
                    (Session_Race_Records.last_name == subquery.c.last_name) &
                    (Session_Race_Records.finishtime == subquery.c.min_finishtime)
                )

            # Apply order_by and then limit
            query = query.order_by(Session_Race_Records.finishtime.asc())
            query = query.limit(entries_per_filter)

            # Fetch and process records
            records = query.all()
            for i, record in enumerate(records):
                event_data[f"{combo_name}_{i}"] = format_db_rsp(record)

    else:
        query = Session_Race_Records.query

        if heat:
            query = query.filter(Session_Race_Records.heat == heat)
        if title_1:
            query = query.filter(Session_Race_Records.title_1 == title_1)
        if title_2:
            query = query.filter(Session_Race_Records.title_2 == title_2)

        query = query.filter(Session_Race_Records.finishtime != 0)

        if unique_names:
            # Subquery for unique names with min finishtime
            subquery = query.with_entities(
                Session_Race_Records.first_name,
                Session_Race_Records.last_name,
                func.min(Session_Race_Records.finishtime).label('min_finishtime')
            ).group_by(
                Session_Race_Records.first_name, 
                Session_Race_Records.last_name
            )

            # Main query joins with the subquery
            query = Session_Race_Records.query.join(
                subquery.subquery(),
                (Session_Race_Records.first_name == subquery.c.first_name) &
                (Session_Race_Records.last_name == subquery.c.last_name) &
                (Session_Race_Records.finishtime == subquery.c.min_finishtime)
            )

        # Apply order_by and then limit
        query = query.order_by(Session_Race_Records.finishtime.asc())
        query = query.limit(entries_per_filter)

        # Fetch and process records
        event_order = query.all()

        for k, a in enumerate(event_order):
            event_data[k] = format_db_rsp(a)

    return event_data