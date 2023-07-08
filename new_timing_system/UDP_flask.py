from flask import Flask, render_template, request
from threading import Thread
import asyncio
import socket

app = Flask(__name__)

class EchoServerProtocol:
    def connection_made(self, transport):
        self.transport = transport

    def datagram_received(self, data, addr):
        message = data.decode()
        print(f"Received {message} from {addr}")

async def udp_server():
    print("Starting UDP server")

    loop = asyncio.get_event_loop()

    transport, protocol = await loop.create_datagram_endpoint(
        lambda: EchoServerProtocol(),
        local_addr=('0.0.0.0', 2008))

    try:
        await asyncio.sleep(3600)  # Serve for 1 hour.
    finally:
        transport.close()

def run_udp_server():
    asyncio.run(udp_server())

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        message = request.form.get('message')
        print(f"Sending {message} to UDP server")
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.sendto(message.encode(), ('127.0.0.1', 2008))
    return render_template('index.html')

if __name__ == "__main__":
    udp_server_thread = Thread(target=run_udp_server)
    udp_server_thread.start()
    app.run(debug=True, host="0.0.0.0",port=6543)
