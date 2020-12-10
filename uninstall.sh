#!/usr/bin/env bash

if [ "$EUID" -ne 0 ]
  then echo "This script must be run as root. Please use 'sudo'."
  exit
fi

/bin/echo stopping scan_monitor.service
/bin/systemctl stop scan_monitor

/bin/echo removing unit file and reloading daemon
/bin/rm /etc/systemd/system/scan_monitor.service
/bin/systemctl daemon-reload

/bin/echo removing /opt/scan_monitor folder
/bin/rm -rf /opt/scan_monitor/

/bin/echo deleting scan_monitor user and group
/usr/sbin/deluser scan_monitor
