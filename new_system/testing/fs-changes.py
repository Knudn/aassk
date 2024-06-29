import os
import time
import shutil
from datetime import datetime
import json
import fcntl

FIFO_PATH = '/tmp/file_monitor_fifo'

def create_fifo():
    if not os.path.exists(FIFO_PATH):
        os.mkfifo(FIFO_PATH)

def open_fifo():
    try:
        fd = os.open(FIFO_PATH, os.O_WRONLY | os.O_NONBLOCK)
        return os.fdopen(fd, 'w')
    except OSError:
        return None

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

def notify_change(fifo, file_path):
    if fifo:
        try:
            message = json.dumps({"changed_file": file_path, "timestamp": datetime.now().isoformat()})
            fcntl.flock(fifo, fcntl.LOCK_EX | fcntl.LOCK_NB)
            fifo.write(message + '\n')
            fifo.flush()
            fcntl.flock(fifo, fcntl.LOCK_UN)
            print(f"Notified change for {file_path}")
        except BlockingIOError:
            print("No FIFO reader available. Skipping notification.")
        except Exception as e:
            print(f"Error writing to FIFO: {e}")

def monitor_files(source_dir, intermediate_dir, use_fifo=False, interval=1):
    files = list_files(source_dir)
    last_modified_times = {file: None for file in files}
    fifo = None

    if use_fifo:
        create_fifo()

    try:
        while True:
            if use_fifo and fifo is None:
                fifo = open_fifo()

            for file in files:
                current_mtime = get_file_modification_time(file)
                
                if current_mtime is None:
                    continue
                
                if last_modified_times[file] is None or current_mtime > last_modified_times[file]:
                    print(f"File changed: {file} at {datetime.fromtimestamp(current_mtime)}")
                    dest_path = os.path.join(intermediate_dir, os.path.basename(file))
                    if copy_file(file, dest_path):
                        if use_fifo:
                            notify_change(fifo, file)
                        last_modified_times[file] = current_mtime

            time.sleep(interval)
    finally:
        if fifo:
            fifo.close()

def main():
    source_directory = '/mnt/test'
    intermediate_directory = '/mnt/intermediate'
    use_fifo = True
    monitor_files(source_directory, intermediate_directory, use_fifo)

if __name__ == "__main__":
    main()