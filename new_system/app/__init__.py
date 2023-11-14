from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from app.lib.db_operation import map_database_files
from flask_socketio import SocketIO

# Initialize SQLAlchemy and SocketIO with no settings
db = SQLAlchemy()
socketio = SocketIO()

def create_app():
    app = Flask(__name__)
    
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////home/rock/aassk/new_system/site.db'
    app.config['SECRET_KEY'] = 'your_secret_key'

    db.init_app(app)
    socketio.init_app(app)

    from app.views.index_view import index_bp
    from app.views.admin_view import admin_bp
    from app.views.api_view import api_bp
    from app.views.vmix_view import vmix_bp
    from app.views.board_view import board_bp

    app.register_blueprint(index_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(api_bp)
    app.register_blueprint(vmix_bp)
    app.register_blueprint(board_bp)

    app.jinja_env.filters['tojson'] = jsonify
    
    return app, socketio
