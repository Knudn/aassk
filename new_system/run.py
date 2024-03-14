from app import create_app, db, socketio  # Notice the added socketio import
from app.models import GlobalConfig, ActiveDrivers, SpeakerPageSettings, InfoScreenAssets, MicroServices, CrossConfig
from app.lib.db_operation import update_active_event
import os
import logging
from logging.handlers import RotatingFileHandler
from app.lib.utils import GetEnv, is_screen_session_running, manage_process_screen

pwd = os.getcwd()

def configure_logging(app):
    log_level = logging.INFO 
    log_directory = os.path.join(os.getcwd(), 'logs')
    if not os.path.exists(log_directory):
        os.makedirs(log_directory)
    log_file = os.path.join(log_directory, 'app.log')

    handler = RotatingFileHandler(log_file, maxBytes=10000000, backupCount=5)
    formatter = logging.Formatter('[%(asctime)s] %(levelname)s in %(module)s: %(message)s')
    handler.setFormatter(formatter)

    app.logger.addHandler(handler)
    app.logger.setLevel(log_level)

    # Also log to stdout
    logging.basicConfig(level=log_level, format='[%(asctime)s] %(levelname)s in %(module)s: %(message)s')
    



def create_tables(app):
    with app.app_context():
        db.create_all() 

        GlobalConfig_db = GlobalConfig.query.get(1)
        ActiveDrivers_db = ActiveDrivers.query.get(1)
        SpeakerPageSettings_db = SpeakerPageSettings.query.get(1)
        InfoScreenAssets_db = InfoScreenAssets.query.get(1)
        Cross_db = CrossConfig.query.all()
        MicroServices_db = MicroServices.query.all()

        # If the database do not exist, it will be created here
        if GlobalConfig_db is None:
            app.logger.info('Created default global config')
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
            app.logger.info('Configuring DB for SpeakerPageSettings')
            default_config = SpeakerPageSettings(
                match_parrallel = False,
            )
            db.session.add(default_config)
            db.session.commit()

        if Cross_db == []:
            app.logger.info('Configuring DB for Cross Config')
            default_config = CrossConfig()
            db.session.add(default_config)
            db.session.commit()

        if MicroServices_db == []:
            app.logger.info('MicroService DB init')
            services = [
                ["Msport Proxy", "msport_display_proxy.py"],
                ["Cross Clock Server", "cross_clock_server.py"]
            ]

            for a in services:
                new_entry = MicroServices(
                    name = a[0],
                    path = a[1]
                )
                db.session.add(new_entry)
                manage_process_screen(a[1], "start")
            db.session.commit()
        else:
            for service in MicroServices_db:
                if bool(service.state) == True:
                    manage_process_screen(service.path, "start")
                else: 
                    manage_process_screen(service.path, "stop")

        if InfoScreenAssets_db is None:
            app.logger.info('Infoscreen DB init')
            assets = [
                ["Ladder Active", "http://192.168.1.50:7777/board/ladder"],
                ["Ladder loop 8", "http://192.168.1.50:7777/board/ladder/loop?timer=8"],
                ["Ladder loop 15", "http://192.168.1.50:7777/board/ladder/loop?timer=15"],
                ["Startlist active upcoming", "http://192.168.1.50:7777/board/startlist_simple_upcoming"],
                ["Startlist active", "http://192.168.1.50:7777/board/startlist_simple"],
                ["Startlist loop stige 8", "http://192.168.1.50:7777/board/startlist_simple_loop?event_filter=Stige&timer=8"],
                ["Startlist loop stige 15", "http://192.168.1.50:7777/board/startlist_simple_loop?event_filter=Stige&timer=15"],
                ["Startlist loop kval 8", "http://192.168.1.50:7777/board/startlist_simple_loop?event_filter=Kvalifisering&timer=8"],
                ["Startlist loop kval 15", "http://192.168.1.50:7777/board/startlist_simple_loop?event_filter=Kvalifisering&timer=15"],
                ["Startlist Single Active", "http://192.168.1.50:7777/board/startlist_active_simple_single"],
                ["Startlist Single Active Upcoming", "http://192.168.1.50:7777/board/startlist_active_simple_single?upcoming=true"],
                ["Scoreboard active", "http://192.168.1.50:7777/board/scoreboard"],
                ["Scoreboard loop 8", "http://192.168.1.50:7777/board/scoreboard_c?columns=3&timer=8"],
                ["Scoreboard loop 15", "http://192.168.1.50:7777/board/scoreboard_c?columns=3&timer=15"],
                ["Scoreboard cross all", "http://192.168.1.50:7777/board/scoreboard_cross?all=all"],
                ["Scoreboard cross event", "http://192.168.1.50:7777/vmix/drivers_stats_cross?active=true"],
            ]
            for a in assets:
                new_entry = InfoScreenAssets(
                    name = a[0],
                    asset = a[1]
                )
                db.session.add(new_entry)
            db.session.commit()

        GlobalConfig_db = GetEnv()

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
    app, socketio = create_app()
    configure_logging(app)
    app.logger.info('App started')
    create_tables(app)
    socketio.run(app, debug=True, host="0.0.0.0", port=7777) 
    
