#!/bin/bash

# Variables
remote_user="root"
remote_pass="administrator"
script_file="/home/rock/aassk/tools/init_screens.sh"
echo "asd"
if [ ! -f ~/.ssh/id_rsa ]; then
    echo "Generating a new SSH key pair..."
    ssh-keygen -t rsa
fi

screens=$(cat instances.yaml | yq e -j | jq '.screens[]')

# Loop through each screen instance
for inst in $(echo "${screens}" | jq -c '.'); do

    # Get name, IP, and local_png_dir of the screen
    remote_host=$(echo "${inst}" | jq -r '.slide_client')

    if grep -q "$remote_host" "~/.ssh/known_hosts"; then
        echo "Key added for $remote_host"
        ssh-keyscan $remote_host >> ~/.ssh/known_hosts
    else
        echo "Found key for $remote_host"
    fi
    
    # Copy the public key to the remote host
    echo "Copying the public key to the remote host..."
    sshpass -p "$remote_pass" ssh-copy-id "$remote_user"@"$remote_host"

    # Transfer the script to the remote host
    echo "Transfering the script to the remote host..."
    sshpass -p "$remote_pass" scp -r "screen_assets" "$remote_user"@"$remote_host":~/

    # Execute the script as root on the remote host
    echo "Executing the script as root on the remote host..."
    sshpass -p "$remote_pass" ssh -oStrictHostKeyChecking=no "$remote_user"@"$remote_host" "chmod +x ~/screen_assets/init_screens.sh; bash ~/screen_assets/init_screens.sh"

    echo "Done."

done