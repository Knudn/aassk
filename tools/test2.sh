#!/bin/bash

people=$(jq '.people[]' sample.yaml)

for person in $(echo "${people}" | jq -c '.'); do
  name=$(echo "${person}" | jq -r '.name')
  age=$(echo "${person}" | jq -r '.age')
  email=$(echo "${person}" | jq -r '.email')
  address=$(echo "${person}" | jq -r '.address.street + " " + .address.city + " " + .address.state + " " + .address.zip')

  echo "Name: ${name}"
  echo "Age: ${age}"
  echo "Email: ${email}"
  echo "Address: ${address}"
  echo ""
done
