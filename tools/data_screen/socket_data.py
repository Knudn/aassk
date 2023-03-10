import socket
import re

from _thread import *
import threading

pattern = r'<mode>(\w+)<mode>'

print_lock = threading.Lock()

data_sock = {}

pattern_name_1 = r'<name1>(.*?)</name1>'
pattern_name_2 = r'<name2>(.*?)</name2>'
pattern_time_1 = r'Tone(\d+\.\d+)'
pattern_time_2 = r'Ttwo(\d+\.\d+)'


data_sock = {
    "Driver1": {
        "name": "asd asd",
        "time": "0"
    },
    "Driver2": {
        "name": "asdasd asd",
        "time": "0"
    }
}


def threaded(c):
    while True:
        
        data = c.recv(1024)

        if not data:
            print('Bye')
            print_lock.release()
            break
        
        data = data.decode('iso-8859-1')
        print(data)
        name_1 = re.search(pattern_name_1, data)
        name_2 = re.search(pattern_name_2, data)
        time_1 = re.search(pattern_time_1, data)
        time_2 = re.search(pattern_time_2, data)
        if name_1 and name_2:
            extracted_name_1 = name_1.group(1).strip().replace('  ', ' ')
            extracted_name_2 = name_2.group(1).strip().replace('  ', ' ')
            extracted_name_1 = ' '.join(extracted_name_1.split())
            extracted_name_2 = ' '.join(extracted_name_2.split())
            data_sock["Driver1"]["name"] = extracted_name_1
            data_sock["Driver2"]["name"] = extracted_name_2
        if time_1 and time_2:
            extracted_time_1 = time_1.group(1)
            extracted_time_2 = time_2.group(1)
            data_sock["Driver1"]["time"] = extracted_time_1
            data_sock["Driver2"]["time"] = extracted_time_2
            print(data_sock)
    c.close()
 
 
def Main():
    host = "192.168.1.50"
 
    port = 7000
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((host, port))
    print("socket binded to port", port)
 
    s.listen(5)
    print("socket is listening")
 
    while True:
 
        c, addr = s.accept()
 
        print_lock.acquire()
        print('Connected to :', addr[0], ':', addr[1])
 
        start_new_thread(threaded, (c,))
    s.close()
 
 
if __name__ == '__main__':
    Main()