#!/bin/bash

# Get screens data from instances.json
screens=$(yq e -j instances.json | jq '.screens[]')
echo $screens

# Loop through each screen instance
for inst in $(echo "${screens}" | jq -c '.'); do

  # Get name, IP, and local_png_dir of the screen
  name=$(echo "${inst}" | jq -r '.name')
  ip=$(echo "${inst}" | jq -r '.ip')
  local_png_dir=$(echo "${inst}" | jq -r '.local_png_dir')
  slide_client=$(echo "${inst}" | jq -r '.slide_client')
  res=$(echo "${inst}" | jq -r '.res')

done
