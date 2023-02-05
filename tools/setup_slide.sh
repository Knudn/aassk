#!/bin/bash

# Add repository for yq tool
add-apt-repository ppa:rmescandon/yq -y

# Update packages and install required software
apt update
apt install postgresql postgresql-contrib jq python3-virtualenv -y

# Create a Python virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Get the current working directory
homedir=$(pwd)

# Install requirements for the slide_app
pip install -r ../slide_app/requirements.txt

# Kill any existing processes using port 5000
netstat -tulpn | grep 5000 | awk '{print $7}' | awk -F "/" '{print $1}' | xargs kill

# Convert instances.yaml to instances.json
cat instances.yaml | yq -j > instances.json

# Get screens data from instances.json
screens=$(jq '.screens[]' instances.json)

# Loop through each screen instance
for inst in $(echo "${screens}" | jq -c '.'); do

  # Get name, IP, and local_png_dir of the screen
  name=$(echo "${inst}" | jq -r '.name')
  ip=$(echo "${inst}" | jq -r '.ip')
  local_png_dir=$(echo "${inst}" | jq -r '.local_png_dir')

  # Remove existing /tmp/$name directory
  rm -rf "/tmp/$name"

  # Copy slide_app to /tmp/$name
  cp -r ../slide_app "/tmp/$name"

  # Run db.sh script with name as argument
  sudo -u postgres ./db.sh $name

  # Add IP address to ens33 interface
  ip address add $ip/255.255.255.0 dev ens33

  # Change to /tmp/$name directory and run Flask app in background
  cd /tmp/$name
  nohup flask run -h $ip -p 5000 > /tmp/$name/$name.log 2>&1 &

  # Create slideshow images directory
  mkdir -p /tmp/$name/slideshow/static/images/slideshow_images/

  # Replace database connection string in config.py
  sed -i -e "s/slideshow:password@database:5432\/slideshow/$name:$name@127.0.0.1:5432\/$name/g" /tmp/$name/config.py

  # Kill any existing pdf_converte.py processes
  ps -aux | grep pdf_converte.py | awk '{print $2}'| xargs kill
  
  # Change back to the original working directory
  cd $homedir

  # Run pdf_converte.py in background
  printf "\nStarting pdf_converte.py for screen '%s'\n" "$name"
  python pdf_converte.py -i $ip -d $local_png_dir 2>&1 &

done

# End of script
printf "\nScript execution completed\n"
