#!/usr/bin/env bash

APP_DIR=/opt/scan_monitor
ACCESS_KEY=[paste your access key here]
SECRET_KEY=[paste your secret key here]

touch ${APP_DIR}/.app_env
chmod 400 $APP_DIR/.app_env

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

cat > ${APP_DIR}/.app_env <<EOF
ACCESS_KEY=$ACCESS_KEY
SECRET_KEY=$SECRET_KEY

POLL_INTERVAL=5

SC_HOST=10.10.102.200
SC_PORT=443

SMTP_SERVER=127.0.0.1
SMTP_SERVER=1025
EOF

useradd --system scan_monitor
chown scan_monitor:scan_monitor $APP_DIR/.app_env

systemctl daemon-reload
