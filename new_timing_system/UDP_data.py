import asyncio
import aioconsole

class EchoServerProtocol(asyncio.DatagramProtocol):
    def __init__(self):
        super().__init__()
        self.transport = None

    def connection_made(self, transport):
        self.transport = transport

    def datagram_received(self, data, addr):
        message = data.decode()
        print(f"Received {data} from {addr}")

async def run_udp_server():
    print("Starting UDP server")
    loop = asyncio.get_running_loop()

    transport, protocol = await loop.create_datagram_endpoint(
        lambda: EchoServerProtocol(),
        local_addr=("192.168.1.50", 2008),
    )

    try:
        while True:
            user_input = await aioconsole.ainput("Enter your input: ")
            print(f"User input: {user_input}")
            protocol.transport.sendto(user_input.encode(), ('192.168.1.33', 2008))
    finally:
        transport.close()

asyncio.run(run_udp_server())
