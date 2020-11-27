#!/usr/bin/env bash

APP_DIR=/opt/scan_monitor

# create virtual env
apt-get install -y python3-venv
python3 -m venv ${APP_DIR}/venv

# install package into virtual env
$APP_DIR/venv/bin/pip install .

# setup systemd unit file
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

useradd --system scan_monitor
chown scan_monitor:scan_monitor $APP_DIR/.env

systemctl daemon-reload
