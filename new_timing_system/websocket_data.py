import asyncio
import websockets
import time
import json
import re
import requests
import sqlite3

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

async def server(ws: str, path: int):
    while True:
        await asyncio.sleep(0.05)
        await ws.send(json.dumps(data_sock, indent=4))


async def handle_client(reader, writer):
    while True:
        await asyncio.sleep(0.05)
        data = await reader.read(4096)
        
       #message = data.decode()
        if data.decode('iso-8859-1') == "":
            pass
        else:
            print(data)
            writer.write(data)
            await asyncio.sleep(0.05)
            await writer.drain()


async def main():
    server = await asyncio.start_server(
        handle_client, '0.0.0.0', 7000)
    async with server:
        await server.serve_forever()


async def start_servers():
    await asyncio.gather(
        websockets.serve(server, '0.0.0.0', 4444),
        main()
    )


asyncio.run(start_servers())
