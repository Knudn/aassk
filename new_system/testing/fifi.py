import os
import time
import shutil
from datetime import datetime
import json

NOTIFICATION_FILE = '/tmp/file_monitor_notifications.txt'

def list_files(directory):
    return [item.path for item in os.scandir(directory) if item.is_file()]

def get_file_modification_time(file_path):
    try:
        return os.path.getmtime(file_path)
    except FileNotFoundError:
        print(f"File not found: {file_path}")
        return None
    except Exception as e:
        print(f"Error checking file {file_path}: {e}")
        return None

def copy_file(src, dest):
    try:
        shutil.copy2(src, dest)
        print(f"Copied {src} to {dest}")
        return True
    except Exception as e:
        print(f"Error copying file {src} to {dest}: {e}")
        return False

def notify_change(file_path):
    try:
        message = json.dumps({
            "changed_file": file_path,
            "timestamp": datetime.now().isoformat()
        })
        with open(NOTIFICATION_FILE, 'a') as f:
            f.write(message + '\n')
        print(f"Notified change for {file_path}")
    except Exception as e:
        print(f"Error writing notification: {e}")

def monitor_files(source_dir, intermediate_dir, use_notifications=False, interval=1):
    files = list_files(source_dir)
    last_modified_times = {file: None for file in files}

    while True:
        for file in files:
            current_mtime = get_file_modification_time(file)
            
            if current_mtime is None:
                continue
            
            if last_modified_times[file] is None or current_mtime > last_modified_times[file]:
                print(f"File changed: {file} at {datetime.fromtimestamp(current_mtime)}")
                dest_path = os.path.join(intermediate_dir, os.path.basename(file))
                if copy_file(file, dest_path):
                    if use_notifications:
                        notify_change(file)
                    last_modified_times[file] = current_mtime

        time.sleep(interval)

def main():
    source_directory = '/mnt/test'
    intermediate_directory = '/mnt/intermediate'
    use_notifications = False  # Set this to True if you want to use notifications
    monitor_files(source_directory, intermediate_directory, use_notifications)

if __name__ == "__main__":
    main()