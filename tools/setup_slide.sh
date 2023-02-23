#!/bin/bash

# Add repository for yq tool
sudo add-apt-repository ppa:rmescandon/yq -y

# Update packages and install required software
#sudo apt update
#sudo apt install yq postgresql postgresql-contrib jq python3-venv gcc libpq-dev python3-wheel python3-dev python3-pip poppler-utils sshpass netplan.io -y

# Create a Python virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Get the current working directory
homedir=$(pwd)

# Install requirements for the slide_app
pip install -r ../slide_app/requirements.txt

# Kill any existing processes using port 5000
sudo netstat -tulpn | grep 5000 | awk '{print $7}' | awk -F "/" '{print $1}' | sudo xargs kill

# Convert instances.yaml to instances.json
cat instances.yaml | yq e -j > instances.json

#Killing the webserver process if it exists
sudo ps -aux | grep "webfsd" | awk '{print $2}' | xargs sudo kill

#Start the webserver
sudo /usr/bin/webfsd -k /var/run/webfs/webfsd.pid -r /share/ -u www-data -g www-data

# Get screens data from instances.json
screens=$(yq e -j instances.json | jq '.screens[]')

# Kill any existing pdf_converte.py processes
sudo ps -aux | grep "pdf_converte.py" | awk '{print $2}'| sudo xargs kill

# Loop through each screen instance
for inst in $(echo "${screens}" | jq -c '.'); do

  # Get name, IP, and local_png_dir of the screen
  name=$(echo "${inst}" | jq -r '.name')
  ip=$(echo "${inst}" | jq -r '.ip')
  local_png_dir=$(echo "${inst}" | jq -r '.local_png_dir')
  slide_client=$(echo "${inst}" | jq -r '.slide_client')
  res=$(echo "${inst}" | jq -r '.res')

  mkdir -p "$local_png_dir/tmp"
  mkdir -p "$local_png_dir/other"
  mkdir -p "$local_png_dir/default/tmp"

  # Remove existing /tmp/$name directory
  sudo rm -rf "/tmp/$name"

  # Copy slide_app to /tmp/$name
  cp -r ../slide_app "/tmp/$name"

  # Run db.sh script with name as argument
  sudo -u postgres ./db.sh $name

  # Add IP address to ens33 interface
  sudo ip address add $ip/255.255.255.0 dev wlan0

  # Change to /tmp/$name directory and run Flask app in background
  cd /tmp/$name
  nohup flask run -h $ip -p 5000 > /tmp/$name/$name.log 2>&1 &

  # Create slideshow images directory
  mkdir -p /tmp/$name/slideshow/static/images/slideshow_images/

  # Replace database connection string in config.py
  sed -i -e "s/slideshow:password@database:5432\/slideshow/$name:$name@127.0.0.1:5432\/$name/g" /tmp/$name/config.py

  # Change back to the original working directory
  cd $homedir

  # Run pdf_converte.py in background
  printf "\nStarting pdf_converte.py for screen '%s'\n" "$name"
  python pdf_converte.py -i $ip -d $local_png_dir -r $res 2>&1 &


done

# End of script
printf "\nScript execution completed\n"
