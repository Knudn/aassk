
from flask import Blueprint, render_template, request, session
import sqlite3
from app.lib.db_operation import reload_event as reload_event_func
from app.lib.db_operation import get_active_event, get_active_event_name
from app.models import Session_Race_Records, ActiveEvents, ActiveDrivers
from app import db
import json
from sqlalchemy import func, and_



vmix_bp = Blueprint('vmix', __name__)


@vmix_bp.route('/vmix/active_driver_stats', methods=['GET'])
def active_driver_stats():
    
    return render_template('vmix/active_driver_dash.html')

@vmix_bp.route('/vmix/active_driver_stats_single', methods=['GET'])
def active_driver_stats_single():
    
    return render_template('vmix/active_driver_dash_single.html')

@vmix_bp.route('/vmix/active_event_json', methods=['GET'])
def active_event_json():
    event_data = get_active_event_name()
    return "{0}, Heat: {1}".format(event_data["title_2"], event_data["heat"])

@vmix_bp.route('/vmix/top_drivers', methods=['GET'])
def top_drivers():
    results = []
    event = get_active_event_name()
    records = Session_Race_Records.query.filter(Session_Race_Records.finishtime > 0, 
                                                Session_Race_Records.penalty == 0,\
                                                Session_Race_Records.title_2 == event["title_2"]) \
                                        .order_by(Session_Race_Records.finishtime.asc())\
                                        .limit(10)\
                                        .all()

    for t in records:
        results.append([t.first_name + " " + t.last_name, t.finishtime])
    
    return render_template('vmix/top_drivers.html', results=results)

@vmix_bp.route('/vmix/results_event_p_loop', methods=['GET'])
def results_event_p_loop():
    from sqlalchemy import case
    session['index'] = session.get('index', 0) + 1


    results = []

    results_orgin = db.session.query(
        Session_Race_Records.title_1,
        Session_Race_Records.title_2,
        func.max(Session_Race_Records.heat).label('max_heat')
    ).filter(
        and_(
            Session_Race_Records.finishtime != 0,
            Session_Race_Records.penalty == 0
        )
    ).group_by(
        Session_Race_Records.title_1,
        Session_Race_Records.title_2
    ).all()

    events = []

    for a in results_orgin:
        if "Finale" in a[1] or "Stige" in a[1]:
            events.append(a)
    

    if len(events) == 0:
        events = results_orgin
    
    event_count = len(events)

    if event_count < session['index']:
        session['index'] = 1

    event_entry = events.pop(session['index'] - 1)
    
    title = event_entry[1] + " " + "Heat: " + str(event_entry[2])
    #('Eikerapen Bakkeløp', 'Trail Unlimited - Finale', 1)

    records_new = Session_Race_Records.query.filter(
        Session_Race_Records.finishtime > 0,
        Session_Race_Records.title_2 == "850 Stock - Kvalifisering",
        Session_Race_Records.heat == event_entry[2]
    ).order_by(
        # Adjusted case statement to comply with SQLAlchemy's current API
        case((Session_Race_Records.penalty != 0, 1), else_=0),
        Session_Race_Records.finishtime.asc()
    ).all()

    count = len(records_new)
    results = []
    results2 = []
    entry_count = 0
    for t in records_new:
        entry_count += 1
        results.append([str(entry_count),t.first_name + " " + t.last_name, t.finishtime, t.penalty, t.snowmobile])

    if count > 20:
        count_data = count//2
        results2 = results[count_data:]
        results = results[:count_data]

    return render_template('vmix/results_event_top_loop.html', results=results, results2=results2, title=title)


@vmix_bp.route('/vmix/results_event', methods=['GET'])
def results_event():
    from sqlalchemy import case

    results = []
    results2 = []

    event = get_active_event_name()
    heat = event["heat"].split("/")[0]
    title = event["title_2"] + " " + "Heat: " + event["heat"]
    records = Session_Race_Records.query.filter(
        Session_Race_Records.finishtime > 0,
        Session_Race_Records.title_2 == event["title_2"],
        Session_Race_Records.heat == heat
    ).order_by(
        # Adjusted case statement to comply with SQLAlchemy's current API
        case((Session_Race_Records.penalty != 0, 1), else_=0),
        Session_Race_Records.finishtime.asc()
    ).all()
    count = len(records)


    entry_count = 0
    for t in records:
        entry_count += 1
        results.append([str(entry_count),t.first_name + " " + t.last_name, t.finishtime, t.penalty, t.snowmobile])

    if count > 20:
        count_data = count//2
        results2 = results[count_data:]
        results = results[:count_data]
    
    return render_template('vmix/results_event.html', results=results, results2=results2, title=title)

@vmix_bp.route('/vmix/get_startlist', methods=['GET'])
def get_startlist():
    from app.lib.utils import GetEnv
    db_location = GetEnv()["db_location"]
    event = get_active_event()
    heat = event[0]["SPESIFIC_HEAT"]

    driver_entries = []

    event_name = get_active_event_name()
    event = get_active_event()

    with sqlite3.connect(db_location + event[0]["db_file"]+".sqlite") as conn:
        cursor = conn.cursor()
        startlist_cid = cursor.execute("SELECT * FROM startlist_r{0};".format(heat)).fetchall()
        drivers = cursor.execute("SELECT * FROM drivers").fetchall()

    count = 0
    driver1 = ""
    driver2 = ""

    for b in range(0,int(len(startlist_cid)/2)):
        for m in drivers:
            if int(startlist_cid[count][1]) == int(m[0]):
                driver1 = m
        for m in drivers:
            if int(startlist_cid[count+1][1]) == int(m[0]):
                driver2 = m
        driver_entries.append((driver1,driver2))
        count = count+2 
    
    title = event_name["title_2"] + " " + event_name["heat"]

    return render_template('vmix/startlist_p.html', results=driver_entries, title=title)

@vmix_bp.route('/vmix/get_startlist_loop', methods=['GET'])
def get_startlist_loop():
    from app.lib.utils import GetEnv

    session['index'] = session.get('index', 0) + 1
    db_location = GetEnv()["db_location"]
    driver_entries = []

    event = get_active_event()
    heat = event[0]["SPESIFIC_HEAT"]
       
    query = db.session.query(ActiveEvents.event_file, ActiveEvents.run, ActiveEvents.mode, ActiveEvents.sort_order, ActiveEvents.event_name).filter(ActiveEvents.run == heat, ActiveEvents.enabled == True).order_by(ActiveEvents.sort_order.asc())
    active_events = query.all()

    event_count = len(active_events)
    
    if event_count < session['index']:
        session['index'] = 1

    event = active_events.pop(session['index'] - 1)

    db_file = event[0]
    heat = event[1]
    title = event.event_name + " Heat: " + str(heat)

    with sqlite3.connect(db_location + db_file +".sqlite") as conn:
        cursor = conn.cursor()
        startlist_cid = cursor.execute("SELECT * FROM startlist_r{0};".format(heat)).fetchall()
        drivers = cursor.execute("SELECT * FROM drivers").fetchall()

    count = 0
    driver1 = ""
    driver2 = ""

    for b in range(0,int(len(startlist_cid)/2)):
        for m in drivers:
            if int(startlist_cid[count][1]) == int(m[0]):
                driver1 = m
        for m in drivers:
            if int(startlist_cid[count+1][1]) == int(m[0]):
                driver2 = m
        driver_entries.append((driver1,driver2))
        count = count+2 
    
    #return "{0}{1}".format(session['index'],event_count)
    return render_template('vmix/startlist_p_loop.html', results=driver_entries, title=title)

@vmix_bp.route('/vmix/get_active_driver_single', methods=['GET'])
def get_active_driver_single():
    from app.lib.utils import GetEnv
    
    query = db.session.query(ActiveDrivers.D1)
    active_driver = query.first()[0]
    event = get_active_event()
    db_file = event[0]["db_file"]
    heat = event[0]["SPESIFIC_HEAT"]
    db_location = GetEnv()["db_location"]

    with sqlite3.connect(db_location + db_file +".sqlite") as conn:
        cursor = conn.cursor()
        drivers = cursor.execute("SELECT * FROM drivers").fetchall()
        driver_stats = cursor.execute("SELECT CID, FINISHTIME FROM driver_stats_r{0};".format(heat)).fetchall()


    for t in drivers:
        if int(active_driver) == int(t[0]):
            driver_name = t[1] + " " + t[2]
            snowmobile = t[4]
            for g in driver_stats:
                if int(g[0]) == int(active_driver):
                    finishtime = g[1]
        

    driver_data = {"NAME":driver_name, "SNOWMOBILE":snowmobile, "FINISHTIME":finishtime/1000}
    
    return driver_data