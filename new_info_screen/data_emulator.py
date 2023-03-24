import socket
from time import sleep
    
clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM);
clientSocket.connect(("192.168.1.50",4445));

d1_name = "<name1>Olav Lok</name1>\n"
d2_name = "<name2>Nøkken Gundersen</name2>\n"
d1_time = 0
d2_time = 0

while True:
    sleep(0.1)

    clientSocket.send(d1_name.encode());
    clientSocket.send(d2_name.encode());
    while True:
        sleep(0.1)
        d1_time += 1
        d2_time += 1
        clientSocket.send(("<time1>"+str(d1_time)+".3"+ "</time1>" +"\n").encode());
        clientSocket.send(("<time2>"+str(d2_time)+".2"+ "</time2>" +"\n").encode());