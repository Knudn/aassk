#!/bin/bash
apt update
apt-get install tigervnc-scraping-server xfce4 xfce4-goodies tightvncserver -y

mkdir -p /home/rock/.vnc
chown rock:rock /home/rock/.vnc

cd screen_assets

echo "Copy Chrome script"
cp chrome_autodeploy.sh /home/rock/chrome.sh
echo "Copy passwd"
cp passwd /home/rock/.vnc/passwd
echo "Copy xstartup"
cp xstartup /home/rock/.vnc/xstartup
echo "Copy slideshow.desktop"
cp slideshow.desktop /home/rock/.config/autostart/slideshow.desktop

chown rock:rock /home/rock/.vnc/passwd
chown rock:rock /home/rock/.vnc/xstartup
chown rock:rock /home/rock/chrome.sh
chown rock:rock /home/rock/.config/autostart/slideshow.desktop


if  grep -q "x0vncserver" "/etc/rc.local" ; then
        echo "x0 entry exists" 
else
        line_number=$(grep -n "exit 0" "/etc/rc.local" | tail -n 1 | awk -F: '{print $1}')
        sudo sed -i "${line_number}i\\sleep 5; su rock -c 'x0vncserver :0 -localhost no -PasswordFile /home/rock/.vnc/passwd'" "/etc/rc.local"
fi

sleep 5
reboot