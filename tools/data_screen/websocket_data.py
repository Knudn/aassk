import asyncio
import websockets
import time
import json
import re
import requests
import sqlite3
con = sqlite3.connect("test.db")
cur = con.cursor()

for row in cur.execute("SELECT * FROM active_drivers"):
    print(row)

cur.execute(""" UPDATE active_drivers
SET c_num = CASE
           WHEN driver = 'Driver_1' THEN 0
           WHEN driver = 'Driver_2' THEN 0
         END;
""")


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



#pattern_name_1 = r'<name1>(.*?)</name1>'
#pattern_name_2 = r'<name2>(.*?)</name2>'
#pattern_time_1 = r'\d+\.\d+'
#pattern_time_2 = r'\d+\.\d+'

pattern_name_1 = r'<name1>(.*?)</name1>'
pattern_name_2 = r'<name2>(.*?)</name2>'
pattern_time_1 = r'Tone(\d+\.\d+)'
pattern_time_2 = r'Ttwo(\d+\.\d+)'
pattern_bid_1 = r'C1(\d+)1C'
pattern_bid_2 = r'C2(\d+)2C'



def data_clean(data):

    
    bid1 = 0
    bid2 = 0
    
    data = data.decode('iso-8859-1')
    print(data)
    name_1 = re.search(pattern_name_1, data)
    name_2 = re.search(pattern_name_2, data)
    time_1 = re.search(pattern_time_1, data)
    time_2 = re.search(pattern_time_2, data)
    bid_1 = re.search(pattern_bid_1, data)
    bid_2 = re.search(pattern_bid_2, data)
   
    if "update_event" in data:
        x = requests.get('http://192.168.1.50:4433/new_event')
        

    if name_1:
        extracted_name_1 = name_1.group(1).strip().replace('  ', ' ')
        extracted_name_1 = ' '.join(extracted_name_1.split())
        data_sock["Driver1"]["name"] = extracted_name_1


    if name_2:

        extracted_name_2 = name_2.group(1).strip().replace('  ', ' ')
        extracted_name_2 = ' '.join(extracted_name_2.split())
        data_sock["Driver2"]["name"] = extracted_name_2

    if bid_1 and bid_2:

        bid1 = bid_1.group(1)
        bid2 = bid_2.group(1)
        print(bid1,bid2)
        cur.execute(""" UPDATE active_drivers
        SET c_num = CASE
                WHEN driver = 'Driver_1' THEN {0}
                WHEN driver = 'Driver_2' THEN {1}
                END;
        """.format(bid1,bid2))
        con.commit()
        x = requests.get('http://192.168.1.50:4433/new_event')


    elif bid_1: 
        bid1 = bid_1.group(1)
        print(bid1)
        cur.execute(""" UPDATE active_drivers
        SET c_num = CASE
                WHEN driver = 'Driver_1' THEN {0}
                WHEN driver = 'Driver_2' THEN {1}
                END;
        """.format(bid1,"0"))
        con.commit()
        x = requests.get('http://192.168.1.50:4433/new_event')

    elif bid_2:
        bid2 = bid_2.group(1)
        print(bid2)
        cur.execute(""" UPDATE active_drivers
        SET c_num = CASE
                WHEN driver = 'Driver_1' THEN {0}
                WHEN driver = 'Driver_2' THEN {1}
                END;
        """.format("0",bid2))

        con.commit()
        x = requests.get('http://192.168.1.50:4433/new_event')


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
        await asyncio.sleep(0.5)
        data = await reader.read(4096)

       #message = data.decode()
        if data.decode('iso-8859-1') == "":
            pass
        else:
            data_clean(data)
            writer.write(data)
            await asyncio.sleep(0.1)
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
