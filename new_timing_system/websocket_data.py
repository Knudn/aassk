import asyncio
import websockets
import time
import json
import re
import requests

data_sock = {
    "Driver1": {
        "name": "None",
        "tmp_name": "false"
    },
    "Driver2": {
        "name": "asdasd asd",
        "time": "0"
    }
}

pattern_name_1 = r'<name1>(.*?)</name1>'
pattern_name_2 = r'<name2>(.*?)</name2>'
driver_name = r'C1(.*?)1C'
new_event = r'<T1>(.*?)</T1>'
tmp_name = ""
keep = False

def data_clean(data): 
    data = data.decode('iso-8859-1')
    #if "\n" in data:
    #    x = requests.get('http://127.0.0.1:8080/update')
    bid1 = 0
    bid2 = 0
    match = re.findall(driver_name, data)
    name_1 = re.search(pattern_name_1, data)
    new_event_match = re.search(new_event, data)

    if new_event_match:
        x = requests.get('http://127.0.0.1:8080/update')
        keep = True

    if name_1:
        extracted_name_1 = name_1.group(1).strip().replace('  ', ' ')
        extracted_name_1 = ' '.join(extracted_name_1.split())

        data_sock["Driver1"]["name"] = extracted_name_1
        
        tmp_name = extracted_name_1
        x = requests.get('http://127.0.0.1:8080/update')

    if match:
        x = requests.get('http://127.0.0.1:8080/update')


    if "update_event" in data or "NEW" in data or "0.0" in data:
        x = requests.get('http://127.0.0.1:8080/update')

    print(data)

async def server(ws: str, path: int):
    while True:
        await asyncio.sleep(0.05)
        await ws.send(json.dumps(data_sock, indent=4))
        

async def handle_client(reader, writer):
    while True:
        await asyncio.sleep(0.15)
        data = await reader.read(4096)

       #message = data.decode()
        if data.decode('iso-8859-1') == "":
            pass
        else:
            data_clean(data)
            writer.write(data)
            await asyncio.sleep(0.15)
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
