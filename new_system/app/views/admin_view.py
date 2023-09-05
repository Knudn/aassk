
from flask import Blueprint, render_template, request, url_for, redirect
from app.lib.db_func import *
from app.lib.utils import GetEnv

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
    elif tab_name == 'microservices':
        return microservices()
    else:
        return "Invalid tab", 404

def home_tab():
    # Logic for home tab
    return render_template('index.html')

def global_config_tab():
    from app.models import GlobalConfig, ConfigForm
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
                db.session.commit()
        else:
            print(full_db_reload())
        return redirect(url_for('admin.admin', tab_name='global-config'))

    return render_template('global_config.html', global_config=global_config, form=form)

def microservices():
    # Logic for test service tab
    return render_template('microservices.html')

