
from flask import Blueprint, render_template, request, url_for, redirect
from app.lib.db_func import *
from app.lib.utils import GetEnv
import json

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/admin/', methods=['GET'])
def admin_home():
    return home_tab()

@admin_bp.route('/admin/ms/<string:tab_name>', methods=['GET','POST'])
def microservices(tab_name):

    if tab_name == 'home':
        return home_tab()
    else:
        return "Invalid tab", 404

@admin_bp.route('/admin/<string:tab_name>', methods=['GET','POST'])
def admin(tab_name):
    if tab_name == 'home':
        return home_tab()
    elif tab_name == 'global-config':
        return global_config_tab()
    elif tab_name == 'microservices':
        return microservices()
    elif tab_name == 'active_events':
        return active_events()
    elif tab_name == 'active_events_driver_data':
        return active_events_driver_data()
    elif tab_name == 'msport_proxy':
        return msport_proxy()
    else:
        return "Invalid tab", 404

def home_tab():
    from app.models import ActiveDrivers
    from app import db


    return render_template('admin/index.html')

def global_config_tab():
    from app.models import GlobalConfig, ConfigForm, ActiveDrivers
    from app import db
    from app.lib.db_func import update_active_event, update_event, update_active_event_stats

    global_config = GlobalConfig.query.all()
    form = ConfigForm()
    
    active_events_data = ActiveDrivers.query.get(1)
    #update_active_event_stats()
    print(active_events_data.Event, active_events_data.Heat )
    
    if form.validate_on_submit():
        if 'submit' in request.form:
            for config in global_config:
                config.session_name = form.session_name.data
                config.project_dir = form.project_dir.data
                config.db_location = form.db_location.data
                config.event_dir = form.event_dir.data
                config.wl_title = form.wl_title.data
                config.wl_bool = bool(form.wl_bool.data)
                config.display_proxy = bool(form.display_proxy.data)
                db.session.commit()
        else:
            print(full_db_reload())
            
        return redirect(url_for('admin.admin', tab_name='global-config'))

    return render_template('admin/global_config.html', global_config=global_config, form=form)

def active_events():
    from app.models import ActiveEvents
    from app import db

    if request.method == 'POST':
        table_data = request.form.get('table_data')
        if table_data:
            try:
                table_data = json.loads(table_data)
                for row in table_data:
                    event = ActiveEvents.query.get(row['id'])
                    if event:
                        event.event_name = row['name']
                        event.run = row['run']
                        event.enabled = row['enable']
                        event.sort_order = row['sort_order']
                db.session.commit()
                return redirect(url_for('admin.admin', tab_name='active_events'))
            except Exception as e:
                print(f"An error occurred: {e}")

    active_events = ActiveEvents.query.order_by(ActiveEvents.sort_order).all()

    return render_template('admin/active_events.html', active_events=active_events)

def active_events_driver_data():
    from app.models import ActiveEvents, GlobalConfig, LockedEntry
    from app import db
    from sqlalchemy import func
    import sqlite3
    import time

    db_location = db.session.query(GlobalConfig.db_location).all()[0][0]

    unique_events = (
        db.session.query(
            ActiveEvents.event_name,
            func.max(ActiveEvents.run).label('max_run'),
            ActiveEvents.event_file
        )
        .group_by(ActiveEvents.event_name).order_by(ActiveEvents.sort_order)
        .all()
    )

    if request.method == 'POST':
        if request.form.get('event_file') is not None:
            selectedEventFile = request.form.get('event_file')
            selectedRun = request.form.get('run')
            event_entry_file = {"file": selectedEventFile, "run": selectedRun}
            print("Getting:", selectedEventFile, selectedRun)
            with sqlite3.connect(db_location + selectedEventFile + ".sqlite") as con:
                cur = con.cursor()
                cur.execute(f"SELECT * FROM driver_stats_r{selectedRun}")

                data = [dict((cur.description[i][0], value) for i, value in enumerate(row)) for row in cur.fetchall()]
                print(data)
            return render_template('admin/active_events_driver_data.html', unique_events=unique_events, sqldata=data, event_entry_file=event_entry_file)

        else:
            
            data = request.get_json()
            file = data["file"]
            run = data["run"]


            db_location = db.session.query(GlobalConfig.db_location).all()[0][0]
            sql_con = sqlite3.connect(db_location + file + ".sqlite")
            
            sql_cur = sql_con.cursor()
            sql_cur.execute(f'DELETE FROM driver_stats_r{run}')

            for a in data["data"]:
                if "LOCKED" in a.keys() and a["LOCKED"] == True:
                    locked = "1"
                else:
                    locked = "0"
                        # Insert the new record
                sql_cur.execute(f'''
                    INSERT INTO driver_stats_r{run} (INTER_1, INTER_2, INTER_3, SPEED, PENELTY, FINISHTIME, CID, LOCKED)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                    (a['INTER_1'], a['INTER_2'], a['INTER_3'], a['SPEED'], a['PENELTY'], a['FINISHTIME'], int(a['CID']), locked)
                )  
            sql_con.commit()
            sql_con.close()
        
        return render_template('admin/active_events_driver_data.html', unique_events=unique_events, sqldata=data, event_entry_file="None")

    return render_template('admin/active_events_driver_data.html', unique_events=unique_events, sqldata="None", event_entry_file="None")

def msport_proxy():

    return render_template('pdfconverter.html')

def microservices():
    # Logic for test service tab
    return render_template('admin/microservices.html')
