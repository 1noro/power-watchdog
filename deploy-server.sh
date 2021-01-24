#!/bin/bash

if [ "$EUID" -ne 0 ]
    then echo "[FAIL] Please run as root or with sudo"
    exit
fi

read -p "Type the name of an existing user to be the one to run the service: " USERNAME

# if id "$1" &>/dev/null; then
#     echo '[INFO] user found'
# else
#     echo "[FAIL] user $USERNAME not found"
#     exit
# fi

ROLE="server"
OPT_FOLDER="/opt/power-watchdog"
UNIT_TEMPLATE="power-watchdog-template.service"
SERVICE_NAME="power-watchdog-$ROLE.service"
UNIT_LOCATION="/etc/systemd/system/$SERVICE_NAME"

mkdir -p "$OPT_FOLDER"
cp "$ROLE.py" "$OPT_FOLDER/$ROLE.py"

chown $USERNAME:$USERNAME "$OPT_FOLDER"

cp "$UNIT_TEMPLATE" "$UNIT_LOCATION"
sed -i "s/@ROLE@/$ROLE/" "$UNIT_LOCATION"
sed -i "s/@USERNAME@/$USERNAME/" "$UNIT_LOCATION"

systemctl enable --now $SERVICE_NAME