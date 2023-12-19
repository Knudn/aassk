from app import create_app, db, socketio  # Notice the added socketio import
from app.models import GlobalConfig, ActiveDrivers, SpeakerPageSettings
from app.lib.db_operation import update_active_event
import os
from app.lib.utils import manage_process, GetEnv

pwd = os.getcwd()
print(pwd)
def create_tables(app):
    with app.app_context():
        db.create_all() 

        GlobalConfig_db = GlobalConfig.query.get(1)
        ActiveDrivers_db = ActiveDrivers.query.get(1)
        SpeakerPageSettings_db = SpeakerPageSettings.query.get(1)

        # If the database do not exist, it will be created here
        if GlobalConfig_db is None:
            default_config = GlobalConfig(
                session_name = "Åseral",
                project_dir = pwd+"/",
                db_location = pwd+"/data/event_db/",
                event_dir = "/mnt/test/",
                wl_title = "Eikerapen",
                infoscreen_asset_path="/app/static/assets/infoscreen"
            )
            db.session.add(default_config)
            db.session.commit()

        if SpeakerPageSettings_db is None:
            default_config = SpeakerPageSettings(
                match_parrallel = False,
            )
            db.session.add(default_config)
            db.session.commit()

        GlobalConfig_db = GetEnv()

        try:

            if GlobalConfig_db["display_proxy"]:
                manage_process("scripts/msport_display_proxy.py", "start")
        except:
            print("Could not get value")


        try:
            active_event,active_heat = update_active_event(GlobalConfig_db)
        except:
            print("Could not get active event")
            active_event = 000
            active_heat = 0

        if ActiveDrivers_db is None:
            default_config = ActiveDrivers(
                D1 = 0,
                D2 = 0,
                Event = active_event,
                Heat = active_heat
            )
            
            db.session.add(default_config)
            db.session.commit()

if __name__ == '__main__':
    app, socketio = create_app()  # Update this line to get both app and socketio



    create_tables(app)
    
    socketio.run(app, debug=True, host="0.0.0.0", port=7777)  # Use socketio.run instead of app.run
