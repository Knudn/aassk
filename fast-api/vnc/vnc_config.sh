#!/bin/bash

x11vnc -passwd PASSWORD -display :0 -wait 50 -noxdamage -auth guess -viewonly -forever &
./vnc/novnc_proxy &