
import os
import hashlib
import time
from pdf2image import *
import sys, getopt
from PIL import Image
from upload import *
import logging
import warnings

warnings.filterwarnings("ignore", category=DeprecationWarning) 

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("debug.log"),
        logging.StreamHandler()
    ]
)
logging.root.setLevel(logging.NOTSET)

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
    return ip, dir_path, res

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
    return [data, images]


def convert_files(path,pdf):
    pages = convert_from_path(path+pdf)
#    for i in range(len(pages)):
#        print(type(i))
    pages[0].save(path+"/tmp/"+pdf +'.jpg', 'JPEG')
    crop_image(path,pdf)

def remove_file(jpg):
    os.remove(dir_path+"/"+b+'.jpg')
    logging.debug("Removed " + dir_path+"/"+b+'.jpg')

def crop_image(path,jpg):
    img = Image.open(path+"/tmp/"+jpg +'.jpg')
#    box = (0, 0, 1875, 1300)
#    img2 = img.crop(box)
    res_image = img.resize(res, Image.ANTIALIAS)
    res_image.save(path + jpg + ".jpg")


if __name__ == "__main__":


    ip, dir_path, res = main(sys.argv[1:])
    curr_data = {}
    curr_images = {}
    default_image = False

    while True: 
    
        old_data = curr_data
        old_images = curr_images
        time.sleep(3)
        curr_data, curr_images = check_files()
        if not curr_data and default_image == False and os.path.isfile("/share/"+dir_path[6:]+"/default/default.jpg"):
            logging.debug("Adding default image")
            try:
                upload(ip,dir_path[6:]+"/default/default.jpg")
            except:
                pass
            default_image = True

        elif curr_data and default_image == True:
            logging.debug("Remove default")
            try:
                remove(ip,dir_path[6:]+"/default/default.jpg")
            except:
                pass
            default_image = False

        #if not curr_data and os.path.isfile(dir_path[6:]+"/default/default.jpg"):
        #    print("false")
        #    upload(ip,dir_path[6:]+"/default/default.jpg")   
        #else:
        #    print("True")
        #    remove(ip,dir_path[6:]+"/default/default.jpg")
            

        if len(old_data) < len(curr_data):
            try:
                logging.info("New file added!")

                for a in curr_data:
                    if curr_data[a] not in old_data.values():
                        logging.debug("Added:" + a)
                        convert_files(dir_path+"/",a)
                        upload(ip,dir_path[6:]+"/"+a+".jpg")
            except:
                pass

        elif len(old_data) > len(curr_data):
            try:
                for b in old_data:
                    if old_data[b] not in curr_data.values():
                        logging.debug("Removed: " + b)
                        remove(ip,dir_path[6:]+"/"+b+".jpg")
                        try:
                            remove_file(dir_path+"/"+b+'.jpg')
                        except:
                            logging.debug(b+".jpg not found in folder, but removed from slideshow database!")
            except:
                pass

        elif str(old_data.values()) != str(curr_data.values()):
            try:
                for a in curr_data:
                    if curr_data[a] not in old_data.values():
                        logging.debug("Replaced:" + a)
                        convert_files(dir_path+"/",a)
                        upload(ip,dir_path[6:]+"/"+a+".jpg")
            except:
                pass

        if len(old_images) < len(curr_images):
            try:
                for a in curr_images:
                    logging.debug(dir_path[6:]+"/other/"+a)
                    if curr_images[a] not in old_images.values():
                        logging.debug("Added:" + a)
                        upload(ip,dir_path[6:]+"/other/"+a)
            except:
                pass

        elif len(old_images) > len(curr_images):
            try:
                for b in old_images:
                    if old_images[b] not in curr_images.values():
                        logging.debug("Removed:" + b)
                        remove(ip,dir_path[6:]+"/other/"+b)
            except:
                pass