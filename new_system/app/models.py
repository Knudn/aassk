from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField
from datetime import datetime
from app import db

class ConfigForm(FlaskForm):
    session_name = StringField('Session Name')
    project_dir = StringField('Project Directory')
    db_location = StringField('Database Location')
    event_dir = StringField('Event Directory')
    wl_title = StringField('Whitelist Title')
    wl_bool = BooleanField('Use Whitelist')
    submit = SubmitField('Save')
    reload = SubmitField('Reload local DB')


class GlobalConfig(db.Model):
    id = db.Column(db.Integer, primary_key=True, default=1)
    session_name = db.Column(db.String(100), nullable=True, default="Åseral")
    project_dir = db.Column(db.String(100), nullable=True, default="/home/rock/aassk/new_timing_system")
    db_location = db.Column(db.String(100), nullable=True, default="/home/rock/aassk/db")
    event_dir = db.Column(db.String(100), nullable=True, default="/mnt/test/")
    wl_title = db.Column(db.String(100), nullable=True, default="Watercross")
    wl_bool = db.Column(db.Boolean, default=True)
