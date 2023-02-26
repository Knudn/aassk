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

pattern_name_1 = r'<name1>(.*?)</name1>'
pattern_name_2 = r'<name2>(.*?)</name2>'
pattern_time_1 = r'\d+\.\d+'
pattern_time_2 = r'\d+\.\d+'

def data_clean(data):
    data = data.decode('iso-8859-1')
    name_1 = re.search(pattern_name_1, data)
    name_2 = re.search(pattern_name_2, data)
    time_1 = re.search(pattern_time_1, data)
    time_2 = re.search(pattern_time_2, data)
    



    if name_1 and name_2:
        extracted_name_1 = name_1.group().strip().replace('  ', ' ')
        extracted_name_2 = name_2.group().strip().replace('  ', ' ')
        extracted_name_1 = ' '.join(extracted_name_1.split())
        extracted_name_2 = ' '.join(extracted_name_2.split())
        data_sock["Driver1"]["name"] = extracted_name_1
        data_sock["Driver2"]["name"] = extracted_name_2
        
    if time_1 and time_2:
        extracted_time_1 = time_1.group(0)
        extracted_time_2 = time_2.group(0)
        if "<time1>" in data:
            data_sock["Driver1"]["time"] = extracted_time_1
        elif "<time2>" in data:
            data_sock["Driver2"]["time"] = extracted_time_2


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
        main()
    )


asyncio.run(start_servers())
