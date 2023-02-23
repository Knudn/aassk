
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
    res = ''
    opts, args = getopt.getopt(argv,"hi:d:r:",["ip=","dir=","resolution="])
    for opt, arg in opts:
        if opt == '-h':
            print ('pdf_converte.py -i <ip address to slideshow> -p <path to filedir> -r <Screen resolution>')
            sys.exit()
        elif opt in ("-i", "--ip"):
            ip = arg
        elif opt in ("-d", "--dir"):
            dir_path = arg
        elif opt in ("-r", "--resolution"):
            res = tuple(map(int, arg.split('x')))
    if ip == '' or dir_path == '' or res == '':
        print ('pdf_converte.py -i <ip address to slideshow> -d <path to filedir> -r <Screen resolution>')
        sys.exit()
    print(ip)
    return ip, dir_path, res

def setup_default():

    for path in os.listdir(dir_path+"/default/"):
        if path[-4:] == ".jpg" or path[-4:] == ".png" or path[-5:] == ".jpeg":
            with open(dir_path + "/default/" +path,'rb') as file:
                chunk = 0
                while chunk != b'':
                    # read only 1024 bytes at a time
                    chunk = file.read(1024)
                    h.update(chunk)
            images[path] = h.hexdigest()
    return [data, images]


def check_files():
    # Iterate directory
    data = {}
    images = {}

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

    for path in os.listdir(dir_path+"/other/"):
        if path[-4:] == ".jpg" or path[-4:] == ".png" or path[-5:] == ".jpeg":
            with open(dir_path + "/other/" +path,'rb') as file:
                chunk = 0
                while chunk != b'':
                    # read only 1024 bytes at a time
                    chunk = file.read(1024)
                    h.update(chunk)
            images[path] = h.hexdigest()


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
#    box = (0, 0, 1875, 1300)
#    img2 = img.crop(box)
    res_image = img.resize(res, Image.ANTIALIAS)
    res_image.save(path + jpg + ".jpg")


if __name__ == "__main__":


    ip, dir_path, res = main(sys.argv[1:])
    print(ip, dir_path)
    curr_data = {}
    curr_images = {}

    while True: 
    
        old_data = curr_data
        if not curr_data:
            upload(ip,dir_path[6:]+"/default/default.jpg")
        else:
            remove(ip,dir_path[6:]+"/default/default.jpg")
            
        old_images = curr_images
        time.sleep(3)
        curr_data, curr_images = check_files()
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
                    try:
                        remove_file(dir_path+"/"+b+'.jpg')
                    except:
                        print(b+".jpg not found in folder, but removed from slideshow database!")
        elif str(old_data.values()) != str(curr_data.values()):
            for a in curr_data:
                if curr_data[a] not in old_data.values():
                    print("Replaced:", a)
                    convert_files(dir_path+"/",a)
                    upload(ip,dir_path[6:]+"/"+a+".jpg")
                    
        if len(old_images) < len(curr_images):
            
            for a in curr_images:
                print(dir_path[6:]+"/other/"+a)
                if curr_images[a] not in old_images.values():
                    print("Added:", a)
                    upload(ip,dir_path[6:]+"/other/"+a)

        elif len(old_images) > len(curr_images):

            for b in old_images:
                if old_images[b] not in curr_images.values():
                    print("Removed:", b)
                    remove(ip,dir_path[6:]+"/other/"+b)
