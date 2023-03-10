import asyncio
import websockets
import time
import json
import re

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


def data_clean(data):
    data = data.decode("utf-8")

async def server(ws: str, path: int):
    while True:
        await asyncio.sleep(0.1)
        await ws.send(json.dumps(data_sock, indent=4))

async def handle_client(reader, writer):
    while True:
        data = await reader.read(1024)
       #message = data.decode()
        data_clean(data)
        writer.write(data)
        await writer.drain()


async def main():
    server = await asyncio.start_server(
        handle_client, '0.0.0.0', 4445)
    async with server:
        await server.serve_forever()


async def start_servers():
    await asyncio.gather(
        websockets.serve(server, '0.0.0.0', 4444),
    )


asyncio.run(start_servers())
