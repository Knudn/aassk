import json
import os
from get_active_event import *
stige_whitelist, normal_whitelist, single_whitelist, all_whitelist = get_white_list()

def generate_json_ladder_current(session=False):

    current = []
    heats = []
    last_data = []
    drivers_set = []
    result_all = []
    full_json = {}
    if session != False:
          event, title = clean_whitelist(session, stige_whitelist)
          current.append(event[:13])
    else:
        with open('startlist/current.json', "r") as json_file:
            current = json.load(json_file)
            print(current[0])
        
    for a in range(1,10):

        if os.path.isfile('startlist/' + current[0] + "_" + str(a) + '_.json'):
            heats.append('startlist/' + current[0] + "_" + str(a) + '_.json')

    with open("startlist/" + current[0] + "_" + "1" + "_.json","r") as data_clear:
        json_str = data_clear.readline()
        json_dict = json.loads(json_str)
        
    for key, value in json_dict.items():
        driver_pair = []

        for i in range(len(value)):
            driver = {"name":value[i][1] + " " + value[i][2], "flag": "au"}
            driver_pair.append(driver)
        drivers_set.append(driver_pair)

    full_json["teams"] = drivers_set
   
    for k,a in enumerate(heats):

        result_set = []

        with open(a,"r") as data_clear:
            
            json_str = data_clear.readline()
            json_dict = json.loads(json_str)

        for key, value in json_dict.items():
            
            if a[-7:] == "2_.json":
                pass
                

            value[0][5] = str(value[0][5])
            value[1][5] = str(value[1][5])
            value[1][7] = round(int(value[1][5]) / 1000, 3)
            value[0][7] = round(int(value[0][5]) / 1000, 3)
            if value[1][6] != 0:
                value[1][7] = 0
            elif value[0][6] != 0:
                value[0][7] = 0


            if a[-7:] == "1_.json":
                result_pair = [value[0][7], value[1][7], "asd", "key", value[0][1] + " " + value[1][1], "not_active"]
                result_set.append(result_pair)


            else:
                for g in last_data:
                    if g == value[0][1]:
                        result_pair = [value[0][7], value[1][7], "asd", "key", value[0][1] + " " + value[1][1], "not_active"]
                        result_set.append(result_pair)
                        break

                    elif g == value[1][1]:
                        result_pair = [value[1][7], value[0][7], "asd", "key", value[1][1] + " " + value[0][1], "not_active"]
                        result_set.append(result_pair)
                        break

            if (int(key) + 1) == len(json_dict.items()):
                last_data = []
                for key, value in json_dict.items():
                    for e in value:
                        last_data.append(e[1])

        result_all.append(result_set)
    full_json["results"] = result_all
    return full_json
