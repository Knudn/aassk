
from flask import Blueprint, render_template, request, url_for, redirect, flash
from app.lib.db_operation import *
from app.lib.utils import GetEnv, intel_sort
import json

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/admin/', methods=['GET'])
def admin_home():
    return home_tab()

@admin_bp.route('/admin/<string:tab_name>', methods=['GET','POST'])
def admin(tab_name):
    if tab_name == 'home':
        return home_tab()
    elif tab_name == 'global-config':
        return global_config_tab()
    elif tab_name == 'infoscreen':
        return infoscreen()
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

    global_config = GlobalConfig.query.all()
    form = ConfigForm()
    
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
            # I'm assuming this is related to the "Reload" button, but you can update as needed
            print(full_db_reload(add_intel_sort=True))
            
        return redirect(url_for('admin.admin', tab_name='global-config'))

    return render_template('admin/global_config.html', global_config=global_config, form=form)


def active_events():
    from app.models import ActiveEvents, EventType, EventOrder, GlobalConfig
    from app import db

    if request.method == 'POST':
        # Handle the form data for table updates
        table_data = request.form.get('table_data')
        sort_data = request.form.get('eventOrderJson')

        # If table_data is provided, process it
        if table_data:
            try:
                table_data = json.loads(table_data)
                print(table_data)
                for k, row in enumerate(table_data):
                    k += 1
                    event = ActiveEvents.query.get(row['id'])
                    if event:
                        event.event_name = row['name']
                        event.run = row['run']
                        event.enabled = row['enable']
                        event.sort_order = k
                db.session.commit()
                flash('Active events updated successfully.', 'success')
            except Exception as e:
                db.session.rollback()  # Rollback in case of error
                flash(f'An error occurred: {e}', 'error')
        
        # If sort_data is provided, process it to update the sort order
        elif sort_data:
            try:
                EventType.query.delete()
                EventOrder.query.delete()
                # Insert EventTypes
                sort_data = json.loads(sort_data)
                for event_type in sort_data['eventTypes']:
                    new_event_type = EventType(
                        order=event_type['order'],
                        name=event_type['name'],
                        finish_heat=event_type['finishHeat']
                    )
                    db.session.add(new_event_type)
                
                # Insert EventOrders
                for event_order in sort_data['eventOrder']:
                    new_event_order = EventOrder(
                        order=event_order['order'],
                        name=event_order['name']
                    )
                    db.session.add(new_event_order)
                
                # Commit the session to save changes
                db.session.commit()
                
            except Exception as e:
                db.session.rollback()  # Rollback in case of error
                flash(f'An error occurred while updating the sort order: {e}', 'error')
            intel_sort()

        elif "smartSortingEnabled" in request.get_json():
            data = request.get_json()['smartSortingEnabled']
            global_config = GlobalConfig.query.first()
            global_config.Smart_Sorting = bool(data)
            db.session.commit()

            if bool(data) == False:
                active_events = ActiveEvents.query.all()

                # Update sort_order to match the id for each event
                for event in active_events:
                    event.sort_order = event.id

                # Commit the changes to the database
                db.session.commit()
                
                
        return redirect(url_for('admin.admin', tab_name='active_events'))

    # For GET requests or after POST processing, retrieve and display the active events
    active_events = ActiveEvents.query.order_by(ActiveEvents.sort_order).all()
    event_types = EventType.query.order_by(EventType.order).all()
    event_order = EventOrder.query.order_by(EventOrder.order).all()
    global_config_new = GlobalConfig.query.first()

    return render_template('admin/active_events.html', active_events=active_events, event_types=event_types, event_order=event_order, global_config_new=global_config_new)

def active_events_driver_data():
    from app.models import ActiveEvents, GlobalConfig, LockedEntry
    from app import db
    from sqlalchemy import func
    import sqlite3
    import time
    from app.lib.db_operation import get_active_event

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
            if request.form.get('event_file') == "active_event":
                active_event = get_active_event()
                selectedEventFile = active_event[0]["db_file"]
                selectedRun = active_event[0]["SPESIFIC_HEAT"]
            else:
                selectedEventFile = request.form.get('event_file')
                selectedRun = request.form.get('run')
            event_entry_file_picked = {"file": selectedEventFile, "run": selectedRun}
            print("Getting:", selectedEventFile, selectedRun)
            with sqlite3.connect(db_location + selectedEventFile + ".sqlite") as con:
                cur = con.cursor()
                cur.execute(f"SELECT * FROM driver_stats_r{selectedRun}")

                data = [dict((cur.description[i][0], value) for i, value in enumerate(row)) for row in cur.fetchall()]
                cur.execute(f"SELECT TITLE1, TITLE2, MODE FROM db_index")
                event_title = cur.fetchall()
                event_info = event_title[0][0]+" "+event_title[0][1]+" - Heat: " + str(selectedRun)  + " - Mode: "+ str(event_title[0][2])

            return render_template('admin/active_events_driver_data.html', unique_events=unique_events, sqldata=data, event_entry_file=event_entry_file_picked, returned_event_info=event_info)

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

def infoscreen():
    from app import db
    from app.models import InfoScreenInitMessage, InfoScreenUrlIndex

    info_screen_msg = InfoScreenInitMessage.query.all()
    print(info_screen_msg)
    return render_template('admin/infoscreen.html', info_screen_msg=info_screen_msg)
