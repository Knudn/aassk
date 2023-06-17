import socket

def start_udp_server():
    UDP_IP = "0.0.0.0"
    UDP_PORT = 2008

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((UDP_IP, UDP_PORT))

    while True:
        data, addr = sock.recvfrom(1024)
        print(f"received message: {data} from {addr}")

if __name__ == "__main__":
    start_udp_server()
