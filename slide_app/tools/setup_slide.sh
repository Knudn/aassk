#!/bin/bash

apt update
apt install postgresql postgresql-contrib -y
apt install python3-virtualenv -y

python3 -m venv venv

source venv/bin/activate

pip install -r ../slideshow_project/requirements.txt

#Find running instences
netstat -tulpn | grep 5001 | awk '{print $7}' | awk -F "/" '{print $1}' | xargs kill

#Remove old data
rm -rf /tmp/slide1
rm -rf /tmp/slide2
rm -rf /tmp/slide3

#Make tmp data
cp -r ../slideshow_project /tmp/slide1
cp -r ../slideshow_project /tmp/slide2
cp -r ../slideshow_project /tmp/slide3

#Setting up the database
sudo -u postgres ./db.sh slide1
sudo -u postgres ./db.sh slide2
sudo -u postgres ./db.sh slide3

#Adding addresses
ip address add 192.168.10.204/255.255.255.0 dev ens33
ip address add 192.168.10.205/255.255.255.0 dev ens33
ip address add 192.168.10.206/255.255.255.0 dev ens33

#Amount of instences
cd /tmp/slide1; nohup flask run -h 192.168.10.204 > slide1_log.txt 2>&1 &
cd /tmp/slide2; nohup flask run -h 192.168.10.205 > slide2_log.txt 2>&1 &
cd /tmp/slide3; nohup flask run -h 192.168.10.206 > slide3_log.txt 2>&1 &

#Create folder
mkdir -p /tmp/slide1/slideshow/static/images/slideshow_images/
mkdir -p /tmp/slide2/slideshow/static/images/slideshow_images/
mkdir -p /tmp/slide3/slideshow/static/images/slideshow_images/

#Replaces the database config
sed -i -e 's/slideshow:password@database:5432\/slideshow/slide1:slide1@127.0.0.1:5432\/slide1/g' /tmp/slide1/config.py
sed -i -e 's/slideshow:password@database:5432\/slideshow/slide2:slide2@127.0.0.1:5432\/slide2/g' /tmp/slide2/config.py
sed -i -e 's/slideshow:password@database:5432\/slideshow/slide3:slide3@127.0.0.1:5432\/slide3/g' /tmp/slide3/config.py

