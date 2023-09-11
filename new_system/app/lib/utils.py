def GetEnv():
    from app.models import GlobalConfig

    global_config = GlobalConfig.query.all()
    
    if not global_config:
        return {}

    first_row = global_config[0]
    row_dict = {key: value for key, value in first_row.__dict__.items() if not key.startswith('_')}

    return row_dict
