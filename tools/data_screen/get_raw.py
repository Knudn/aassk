import socket


def threaded(c):
    while True:
        
        data = c.recv(1024)
        print("asd")
        if not data:
            print('Bye')
            print_lock.release()
            break
        print(data)
        data = data.decode('utf-8')

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