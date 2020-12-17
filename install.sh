#!/usr/bin/env bash

if [ "$EUID" -ne 0 ]
  then echo "This script must be run as root. Please use 'sudo'."
  exit
fi

APP_DIR=/opt/scan_monitor
SRC_DIR=$(dirname "$0")

# install system dependencies
/usr/bin/apt update
/usr/bin/apt install -y python3-pip python3-venv python3-systemd

/bin/echo "*** Installing scan_monitor into $APP_DIR"
# add scan monitor user
/usr/sbin/adduser --quiet --home $APP_DIR --gecos "" --disabled-login scan_monitor

# create log directory
/bin/mkdir -p $APP_DIR/var/log
/usr/bin/touch $APP_DIR/var/log/notify.log
# install the virtual environment and append 'activate' to .bash_profile
/usr/bin/python3 -m venv "$APP_DIR"
/usr/bin/echo "source $APP_DIR/bin/activate" > "$APP_DIR/.bash_profile"

# copy templates
/bin/cp -r "$SRC_DIR/scan_monitor/templates" "$APP_DIR"

# install wheel and scan_monitor into virtual env
$APP_DIR/bin/pip install wheel
$APP_DIR/bin/pip install "$SRC_DIR"

# setup systemd unit file and do a daemon-reload
/usr/bin/cat > /etc/systemd/system/scan_monitor.service <<EOF
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

# create ENV_FILE with some defaults and set permissions
ENV_FILE=$APP_DIR/.monitor_env
/usr/bin/cat > $ENV_FILE << EOF
TSC_PORT=443
SMTP_PORT=25
POLL_INTERVAL=15
EOF
/bin/chown -R scan_monitor:scan_monitor $APP_DIR
/bin/chmod 400 $ENV_FILE

/bin/echo "###                                                                        "
/bin/echo "###  Installation complete.                                                "
/bin/echo "###                                                                        "
/bin/echo "###  Next, run the configure command to configure application settings.    "
/bin/echo "###                                                                        "
/bin/echo "###     sudo $APP_DIR/bin/configure                                        "
/bin/echo "###                                                                        "
/bin/echo "###                                                                        "
/bin/echo "###  After completing the configuration, start the monitor with the        "
/bin/echo "###  following command:                                                    "
/bin/echo "###                                                                        "
/bin/echo "###     sudo /bin/systemctl start scan_monitor                             "
/bin/echo "###                                                                        "
