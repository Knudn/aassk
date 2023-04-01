import json
import os


def generate_json_ladder_current(active_drivers):


    start_list = {}
    current = []
    heats = []
    last_data = []
    teams = []
    drivers_set = []
    result_all = []
    full_json = {}


    with open('startlist/current.json', "r") as json_file:
        current = json.load(json_file)
    
    for a in range(1,10):

        if os.path.isfile('startlist/' + current[0] + "_" + str(a) + '_.json'):
            heats.append('startlist/' + current[0] + "_" + str(a) + '_.json')

    with open("startlist/" + current[0] + "_" + "1" + "_.json","r") as data_clear:
        json_str = data_clear.readline()
        json_dict = json.loads(json_str)
        
    for key, value in json_dict.items():
        driver_pair = []

        for i in range(len(value)):
            driver = {"name":value[i][1], "flag": "au"}
            driver_pair.append(driver)
        drivers_set.append(driver_pair)

    full_json["teams"] = drivers_set
    
    for a in heats:
        result_set = []
        
        with open(a,"r") as data_clear:
            
            json_str = data_clear.readline()
            json_dict = json.loads(json_str)

        for key, value in json_dict.items():
            pait = []
            
            
            if a[-7:] == "2_.json":

                print(last_data)

            
            value[0][5] = str(value[0][5])
            value[1][5] = str(value[1][5])
            value[1][7] = round(int(value[1][5]) / 1000, 3)
            value[0][7] = round(int(value[0][5]) / 1000, 3)
            if value[1][6] != 0:
                value[1][7] = 0
            elif value[0][6] != 0:
                value[0][7] = 0

            
            #b[5] = str(seconds) + "." + str(milliseconds)
            #if value[0][0] in active_drivers and value[1][0] in active_drivers:
            #    result_pair = [value[0][7], value[1][7], "asd", "key", value[0][1] + " " + value[0][1] , "active"]
            #else:
            last_data.append(value)
            result_pair = [value[0][7], value[1][7], "asd", "key", value[0][1] + " " + value[1][1], "not_active"]
            result_set.append(result_pair)

        result_all.append(result_set)
    full_json["results"] = result_all
    return full_json
def generate_json_ladder_current_new(active_drivers):

    pass
