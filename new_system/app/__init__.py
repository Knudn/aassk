from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from app.lib.db_func import map_database_files

# Initialize SQLAlchemy with no settings
db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////home/rock/aassk/new_system/site.db'
    app.config['SECRET_KEY'] = 'your_secret_key'
    
    db.init_app(app)

    from app.views.index_view import index_bp
    from app.views.admin_view import admin_bp
    from app.views.api_view import api_bp
    from app.views.vmix_view import vmix_bp

    app.register_blueprint(index_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(api_bp)
    app.register_blueprint(vmix_bp)

    app.jinja_env.filters['tojson'] = jsonify
    
    return app
    