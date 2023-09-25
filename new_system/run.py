from app import create_app, db
from app.models import GlobalConfig, ActiveDrivers
from app.lib.db_func import get_active_data
import os
from app.lib.utils import manage_process, GetEnv

pwd = os.getcwd()

def create_tables(app):
    with app.app_context():
        db.create_all() 

        GlobalConfig_db = GlobalConfig.query.get(1)
        ActiveDrivers_db = ActiveDrivers.query.get(1)

        #If the database do not exist, it will be created here
        if GlobalConfig_db is None:
            default_config = GlobalConfig(
                session_name = "Åseral",
                project_dir = pwd+"/",
                db_location = pwd+"/data/event_db/",
                event_dir = "/mnt/test/",
                wl_title = "Eikerapen"
            )
            db.session.add(default_config)
            db.session.commit()

        GlobalConfig_db = GetEnv()

        if GlobalConfig_db["display_proxy"]:
            manage_process("scripts/msport_display_proxy.py", "start")

        active_event,active_heat = get_active_data(GlobalConfig_db)

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
    app = create_app()
    
    create_tables(app)
    
    app.run(debug=True, host="0.0.0.0", port=7777)