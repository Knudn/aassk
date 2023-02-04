#!/usr/bin/python3

import os
import hashlib
import time
from pdf2image import *
import sys
from PIL import Image

# folder path
dir_path = r'/share/Skjerm1'

def check_files():
    # Iterate directory
    data = {}
    h = hashlib.sha1()
    for path in os.listdir(dir_path):
        if os.path.isfile(os.path.join(dir_path, path)):
            if path[-4:] == ".pdf":
                with open(dir_path + "/" +path,'rb') as file:
                    chunk = 0
                    while chunk != b'':
                        # read only 1024 bytes at a time
                        chunk = file.read(1024)
                        h.update(chunk)
                data[path] = h.hexdigest()
    return data

def convert_files(path,pdf):
    pages = convert_from_path(path+pdf)
#    for i in range(len(pages)):
#        print(type(i))
    pages[0].save(path+"/tmp/"+pdf +'.jpg', 'JPEG')
    crop_image(path,pdf)

def remove_file(jpg):
    os.remove(dir_path+"/"+b+'.jpg')
    print("Removed " + dir_path+"/"+b+'.jpg')

def crop_image(path,jpg):
    img = Image.open(path+"/tmp/"+jpg +'.jpg')
    box = (0, 0, 1875, 1300)
    img2 = img.crop(box)
    img2.save(path + jpg + ".jpg")

curr_data = check_files()

while True: 
    
    old_data = curr_data
    time.sleep(3)
    curr_data = check_files()

    if old_data != curr_data:
        print("Changed found!")
        
        for a in curr_data:
            if not old_data:
                print("Added:", a)
                convert_files(dir_path+"/",a)

            for b in old_data:
                if curr_data[a] not in old_data.values():
                    print("Added:", a)
                    convert_files(dir_path+"/",a)
                    break
                elif old_data[b] not in curr_data.values():
                    try:
                        print("Removed:", b)
                        remove_file(dir_path+"/"+b+'.jpg')
                        break
                    except:
                        print("Failed")
                    
                    


