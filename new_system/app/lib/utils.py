def GetEnv():
    from app.models import GlobalConfig

    global_config = GlobalConfig.query.all()
    
    if not global_config:
        return {}

    first_row = global_config[0]
    row_dict = {key: value for key, value in first_row.__dict__.items() if not key.startswith('_')}

    return row_dict

def SMBServer(smbdb):
    from app.models import GlobalConfig
    import os
    import sys
    import subprocess

    global_config = GlobalConfig.query.get(1)
    python_executable = sys.executable

    if smbdb.state == True:
        print(global_config.project_dir)
        print(smbdb.name)
        
        script_to_run = global_config.project_dir+"app/lib/smbserver.py"

        smb_path = smbdb.smb_path
        smb_name = smbdb.smb_name
        smb_port = "-port " + str(smbdb.smb_port)
        
        subprocess.run([python_executable, script_to_run, smb_port, smb_name, smb_path])

def pdf_converter(pdfconfig):
    from app.models import GlobalConfig
    import os
    import sys
    import subprocess
    import signal

    global_config = GlobalConfig.query.get(1)
    python_executable = sys.executable

    process = None

    if pdfconfig.state == True:
        script_to_run = os.path.join(global_config.project_dir, "app/lib/pdf_converte.py")
        pdf_path_dir = pdfconfig.path_dir
        kill_process_by_command(script_to_run)
        process = subprocess.Popen([python_executable, script_to_run, pdf_path_dir])

    return process

def kill_process_by_command(command_pattern):
    import psutil
    for proc in psutil.process_iter(attrs=['pid', 'cmdline']):
        try:
            cmdline = ' '.join(proc.info['cmdline'])
            if command_pattern in cmdline:
                psutil.Process(proc.info['pid']).terminate()
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass