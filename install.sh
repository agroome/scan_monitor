#!/usr/bin/env bash

if [ "$EUID" -ne 0 ]
  then echo "This script must be run as root. Please use 'sudo'."
  exit
fi

APP_DIR=/opt/scan_monitor

# create virtual environment in APP_DIR
if [[ ! -d "$APP_DIR" ]]; then
  /bin/echo "*** Installing libraries in $APP_DIR"
  /usr/bin/apt install -y python3-venv python3-systemd
  python3 -m venv "$APP_DIR"
fi

# install scan_monitor into virtual env
SRC_DIR=$(dirname "$0")
$APP_DIR/bin/pip install -U "$SRC_DIR"

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
ExecStart=$APP_DIR/bin/scan_monitor

[Install]
WantedBy=multi-user.target
EOF
    /bin/systemctl daemon-reload
fi

if ! id scan_monitor > /dev/null 2>&1; then
  /bin/echo "creating scan_monitor user"
  /usr/sbin/useradd --system scan_monitor
fi

# setup folders and config file
if [[ ! -d "$APP_DIR"/etc ]]; then
  /bin/mkdir -p "$APP_DIR"/etc
  /bin/cp "$SRC_DIR"/config.json.sample "$APP_DIR"/etc/config.json
fi

# set ownership and ensure read permsisions are restricted on config.json
/bin/chown scan_monitor:scan_monitor -R "$APP_DIR"
/bin/chmod 400 "$APP_DIR"/etc/config.json

/bin/echo "###  Installation complete. "
/bin/echo "### "
/bin/echo "###  Edit the values in /opt/scan_monitor/etc/config.json suit your environment. You will need: "
/bin/echo "###    - Tenable.sc API key pair "
/bin/echo "###    - Tenable.sc IP address or hostname and port "
/bin/echo "###    - SMTP ServerTenable.sc IP address or hostname and port "
/bin/echo "###    - Email 'from_address'"
/bin/echo "###  "
/bin/echo "###  After editing config.json, start the scan_monitor service: "
/bin/echo "###  "
/bin/echo "###  sudo /bin/systemctl start scan_monitor"
/bin/echo "###  "
