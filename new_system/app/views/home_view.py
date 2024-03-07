
from flask import Blueprint, render_template, request
import sqlite3
from app.lib.db_operation import reload_event as reload_event_func


home_bp = Blueprint('home', __name__)


@home_bp.route('/home/home', methods=['GET'])
def homepage():
    return render_template('home/index.html')

@home_bp.route('/home/cross', methods=['GET'])
def home_cross():
    return render_template('home/cross.html')

@home_bp.route('/home/startlist', methods=['GET'])
def home_startlist():
    return render_template('home/startlist.html')

@home_bp.route('/home/ladder', methods=['GET'])
def home_ladder():
    return render_template('home/ladder.html')

@home_bp.route('/home/results', methods=['GET'])
def home_results():
    return render_template('home/results.html')
