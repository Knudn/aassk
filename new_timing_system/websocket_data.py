import asyncio
import websockets
import time
import json
import re
import requests



pattern_name_1 = r'<name1>(.*?)</name1>'
pattern_name_2 = r'<name2>(.*?)</name2>'


def data_clean(data):

    
    bid1 = 0
    bid2 = 0
    
    data = data.decode('iso-8859-1')

    print(data)
    if "update_event" in data or "NEW" in data:
        x = requests.get('http://127.0.0.1:8080/update')


async def server(ws: str, path: int):
    while True:
        await asyncio.sleep(0.05)

async def handle_client(reader, writer):
    while True:
        await asyncio.sleep(0.05)
        data = await reader.read(4096)

       #message = data.decode()
        if data.decode('iso-8859-1') == "":
            pass
        else:
            data_clean(data)
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
