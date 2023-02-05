
import os
import hashlib
import time
from pdf2image import *
import sys, getopt
from PIL import Image
from upload import *

def main(argv):

    ip = ''
    dir_path = ''
    opts, args = getopt.getopt(argv,"hi:d:",["ip=","dir="])
    for opt, arg in opts:
        if opt == '-h':
            print ('pdf_converte.py -i <ip address to slideshow> -p <path to filedir>')
            sys.exit()
        elif opt in ("-i", "--ip"):
            ip = arg
        elif opt in ("-d", "--dir"):
            dir_path = arg
    if ip == '' or dir_path == '':
        print ('pdf_converte.py -i <ip address to slideshow> -d <path to filedir>')
        sys.exit()
    return ip, dir_path

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


if __name__ == "__main__":

    ip, dir_path = main(sys.argv[1:])
    print(ip, dir_path)
    curr_data = {}

    while True: 
        
        old_data = curr_data
        time.sleep(3)
        curr_data = check_files()
        try:
            if len(old_data) < len(curr_data):
                print("New file added!")

                for a in curr_data:
                    if curr_data[a] not in old_data.values():
                        print("Added:", a)
                        convert_files(dir_path+"/",a)
                        upload(ip,dir_path[6:]+"/"+a+".jpg")

            elif len(old_data) > len(curr_data):

                for b in old_data:
                    if old_data[b] not in curr_data.values():
                        print("Removed:", b)
                        remove(ip,dir_path[6:]+"/"+b+".jpg")
                        remove_file(dir_path+"/"+b+'.jpg')
            elif str(old_data.values()) != str(curr_data.values()):
                for a in curr_data:
                    if curr_data[a] not in old_data.values():
                        print("Replaced:", a)
                        convert_files(dir_path+"/",a)
                        upload(ip,dir_path[6:]+"/"+a+".jpg")
        except:
            print("Shit hit the fan...")
