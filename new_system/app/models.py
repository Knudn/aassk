from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField, IntegerField
from datetime import datetime
from app import db

class InfoScreenInitMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    hostname = db.Column(db.String(128), nullable=False)
    ip = db.Column(db.String(15), nullable=False)
    unique_id = db.Column(db.String(32), nullable=False)
    approved = db.Column(db.String(6), nullable=False, default=False)

    def __repr__(self):
        return f'<InitMessage {self.hostname} {self.ip} {self.unique_id} {self.approved}>'

class InfoScreenUrlIndex(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(32), nullable=False)
    loop = db.Column(db.Boolean, nullable=False)

    def __repr__(self):
        return f'<InitMessage {self.unique_id} {self.url} {self.loop}>'

class ConfigForm(FlaskForm):
    session_name = StringField('Session Name')
    project_dir = StringField('Project Directory')
    db_location = StringField('Database Location')
    event_dir = StringField('Event Directory')
    wl_title = StringField('Whitelist Title')
    wl_bool = BooleanField('Use Whitelist')
    display_proxy = BooleanField('Use MSport display proxy')
    submit = SubmitField('Save')
    reload = SubmitField('Reload local DB')

class GlobalConfig(db.Model):
    id = db.Column(db.Integer, primary_key=True, default=1)
    session_name = db.Column(db.String(100), nullable=True, default="Åseral")
    project_dir = db.Column(db.String(100), nullable=True, default="/home/rock/aassk/new_timing_system")
    db_location = db.Column(db.String(100), nullable=True, default="/home/rock/aassk/new_system/event_db/")
    event_dir = db.Column(db.String(100), nullable=True, default="/mnt/test/")
    wl_title = db.Column(db.String(100), nullable=True, default="Watercross")
    wl_bool = db.Column(db.Boolean, default=True)
    display_proxy = db.Column(db.Boolean, default=True)
    Smart_Sorting = db.Column(db.Boolean, default=False)


class ActiveEvents(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    event_name = db.Column(db.String(100))
    event_file = db.Column(db.String(20))
    run = db.Column(db.Integer)
    enabled = db.Column(db.Integer, default=True)
    sort_order = db.Column(db.Integer)
    mode = db.Column(db.Integer)

    def __repr__(self):
        return (f"<ActiveEvents(id={self.id}, event_name='{self.event_name}', event_file='{self.event_file}', "
                f"run={self.run}, enabled={self.enabled}, sort_order={self.sort_order}, mode={self.mode})>")

class LockedEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    cid = db.Column(db.Integer)
    event_name = db.Column(db.String(100))
    heat = db.Column(db.Integer)

class ActiveDrivers(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Event = db.Column(db.String(20))
    Heat = db.Column(db.String(20))
    D1 = db.Column(db.Integer)
    D2 = db.Column(db.Integer)

class EventType(db.Model):
    __tablename__ = 'event_types'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    order = db.Column(db.Integer, nullable=False)
    name = db.Column(db.String, nullable=False)
    finish_heat = db.Column(db.Boolean, default=False, nullable=False)

    def __repr__(self):
        return f"<EventType(order={self.order}, name='{self.name}', finish_heat={self.finish_heat})>"

class EventOrder(db.Model):
    __tablename__ = 'event_order'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    order = db.Column(db.Integer, nullable=False)
    name = db.Column(db.String, nullable=False)

    def __repr__(self):
        return f"<EventOrder(order={self.order}, name='{self.name}')>"