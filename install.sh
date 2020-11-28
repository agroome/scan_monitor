#!/usr/bin/env bash

APP_DIR=/opt/scan_monitor

# create virtual env
if [[ ! -d ${APP_DIR}/venv ]]; then
  /bin/echo "creating virtual environment ${APP_DIR}/venv"
  /usr/bin/apt install -y python3-venv
  python3 -m venv ${APP_DIR}/venv
fi

# install scan_monitor into virtual env
$APP_DIR/venv/bin/pip install -U .

if [[ ! -d $APP_DIR/var/log ]]; then
  /bin/mkdir -p $APP_DIR/var/log
  /bin/chgrp scan_monitor $APP_DIR/var/log
  /bin/chmod 775 $APP_DIR/var/log
fi

# setup systemd unit file
if [[ ! -f /etc/systemd/system/scan_monitor.service ]]; then
    cat > /etc/systemd/system/scan_monitor.service <<EOF
[Unit]
Description=Scan Monitor
After=multi-user.target

[Service]
User=scan_monitor
Group=scan_monitor

WorkingDirectory=$APP_DIR
ExecStart=$APP_DIR/venv/bin/python scan_monitor.py

[Install]
WantedBy=multi-user.target
EOF
    /bin/systemctl daemon-reload
fi

if ! id scan_monitor > /dev/null 2>&1; then
  /bin/echo "creating scan_monitor user"
  /usr/sbin/useradd --system scan_monitor
fi

if [[ ! -f ${APP_DIR}/config.json ]]; then
  /bin/cp ${APP_DIR}/config.json.sample ${APP_DIR}/config.json
  /bin/chown scan_monitor:scan_monitor ${APP_DIR}/config.json
  /bin/chmod 640 ${APP_DIR}/config.json
fi

/bin/echo "###  Installation complete. "
/bin/echo "### "
/bin/echo "###  Edit the values in config.json suit your environment. This includes Tenable.sc API keys,"
/bin/echo "###  and network address/port information for Tenable.sc and an SMTP relay server. "
/bin/echo "###  "
/bin/echo "###  After editing config.json, start the scan_monitor service: "
/bin/echo "###  $ sudo /bin/systemctl start "
/bin/echo "###  "
