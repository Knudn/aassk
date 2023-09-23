from app import create_app, db
from app.models import GlobalConfig, ActiveDrivers
import os
from app.lib.utils import pdf_converter

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

        if ActiveDrivers_db is None:
            default_config = ActiveDrivers(
                D1 = 0,
                D2 = 0,
            )
            db.session.add(default_config)
            db.session.commit()
        
if __name__ == '__main__':
    app = create_app()
    
    create_tables(app)
    
    app.run(debug=True, host="0.0.0.0", port=7777)