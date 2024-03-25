
import asyncio
import websockets
import re
import json
import sqlite3
import logging
import requests
import socket

# Setting up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')



# Constants
DB_PATH = "site.db"
URL = 'http://localhost:10000/entry'


with sqlite3.connect(DB_PATH) as con:
    cur = con.cursor()
    listen_ip = cur.execute("SELECT params FROM microservices WHERE path = 'msport_display_proxy.py';").fetchone()[0]


#Regex rules
PARRALEL_PATTERNS = {
    "name_1": r'<name1>(.*?)</name1>',
    "name_2": r'<name2>(.*?)</name2>',
    "time_1": r'TO(.*?)OT',
    "time_2": r'TT(.*?)TT',
    "bid_1": r'C1(\d+)1C',
    "bid_2": r'C2(\d+)2C',
    "snowmobile_1": r'POS(.*?)POS',
    "snowmobile_2": r'PTS(.*?)PTS'
}

data_sock = {
    "Driver1": {"name": "", "time": "0"},
    "Driver2": {"name": "", "time": "0"}
}

driver_index = 0

refresh_triggers = ["DNS", "DSQ", "DNF"]

update_field = False

d_history = ""

def update_driver(D1=None, D2=None):
    
    with sqlite3.connect(DB_PATH) as con:
        cur = con.cursor()
        if D1 is not None and D2 is not None:
            cur.execute("UPDATE active_drivers SET D1 = ?, D2 = ?;", (D1, D2))
        elif D1 is not None:
            cur.execute("UPDATE active_drivers SET D1 = ?;", (D1,))
        elif D2 is not None:
            cur.execute("UPDATE active_drivers SET D2 = ?;", (D2,))
        con.commit()
        print(cur.execute("SELECT * FROM active_drivers;").fetchall())

def extract_data(pattern_key, data):
    match = re.search(PARRALEL_PATTERNS[pattern_key], data)
    return match.group(1).strip().replace('  ', ' ') if match else None

def data_clean(data):
    global refresh_triggers
    global driver_index
    global update_field
    global d_history

    data = data.decode('iso-8859-1')
    
    name_1 = extract_data("name_1", data)
    name_2 = extract_data("name_2", data)
    time_1 = extract_data("time_1", data)
    time_2 = extract_data("time_2", data)
    bid_1 = extract_data("bid_1", data)
    bid_2 = extract_data("bid_2", data)
    snowp1 = extract_data("snowmobile_1", data)
    snowp2 = extract_data("snowmobile_2", data)

    print(data)
    if "update" in data:
        update_field = True

    if name_1:
        if d_history != name_1:
            driver_index = 0
        print(name_1, "Name1")
        data_sock["Driver1"]["name"] = name_1
        data_sock["Driver1"]["time"] = 0
        if "FILLER" in name_1:
            driver_index += 1
            if driver_index >= 2:
                update_field = True
    if name_2:
        print(name_2, "Name2")
        data_sock["Driver2"]["name"] = name_2
        data_sock["Driver2"]["time"] = 0
        if "FILLER" in name_2:
            driver_index += 1
            if driver_index >= 2:
                update_field = True

    if bid_1 or bid_2:

        try:
            update_driver(D1=bid_1, D2=bid_2)
            update_field = True
            logging.info("Updated active driver: %s, %s", bid_1, bid_2)

        except:
            logging.info("Could not update drivers: %s, %s", bid_1, bid_2)

    if time_1 and "TO" in data:
        data_sock["Driver1"]["time"] = time_1

        try:
            if len(time_1.split(".")[1]) >= 3:
                driver_index += 1
                if driver_index >= 2:
                    driver_index = 0
                    update_field = True
        except:
            if time_1 in refresh_triggers:
                driver_index += 1
                if driver_index >= 2:
                    driver_index = 0
                    update_field = True

    if time_2 and "TT" in data:

        data_sock["Driver2"]["time"] = time_2

        try:
            if len(time_2.split(".")[1]) >= 3:
                driver_index += 1
                if driver_index >= 2:
                    driver_index = 0
                    update_field = True
        except:
            if time_2 in refresh_triggers:
                driver_index += 1
                if driver_index >= 2:
                    driver_index = 0
                    update_field = True
            

    
    if snowp1 and "POS" in data:
        data_sock["Driver1"]["snowmobile"] = snowp1

    if snowp2 and "PTS" in data:
        data_sock["Driver2"]["snowmobile"] = snowp2
    
    if update_field == True:
        requests.get("http://{0}:7777/api/active_event_update".format(listen_ip))
        update_field = False

async def server(ws, path):
    while True:
        await asyncio.sleep(0.05)
        await ws.send(json.dumps(data_sock, indent=4))

async def handle_client(reader, writer):
    
    while True:
        await asyncio.sleep(0.05)
        data = await reader.read(4096)
        decoded_data = data.decode('iso-8859-1')
        if decoded_data:
            data_clean(data)
            writer.write(data)
            await asyncio.sleep(0.05)
            await writer.drain()

async def main():
    print(listen_ip)
    server = await asyncio.start_server(handle_client, listen_ip, 7000)

    async with server:
        await server.serve_forever()

async def start_servers():
    await asyncio.gather(websockets.serve(server, '0.0.0.0', 4444), main())

if __name__ == '__main__':
    asyncio.run(start_servers())
