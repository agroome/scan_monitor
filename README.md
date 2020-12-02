# scan_monitor

Monitor and report on the status of Tenable.sc scans. scan_monitor polls the Tenable.sc API and send a notification
email to a list of users when a scan instance changes to one of the following states: 
 'Running', 'Paused', 'Completed', 'Partial', or 'Error'.
 
Email recipients are defined in a meta-data section that can be appended to the bottom of the scan 
description. Meta-data in the following format will be recognized:

```
--- do not delete below this line ---
[notifications]
email: user1@example.com, user2@example.com, user3@example.com 
```

*** This tool is not an officially supported Tenable project.                   
*** Use of this tool is subject to the terms and conditions identified in the [LICENSE](LICENSE) file,  
*** and is not subject to any license agreement you may have with Tenable 

## Installation

Clone the repository into /opt/scan_monitor:
```
sudo git clone https://github.com/agroome/scan_monitor /opt/scan_monitor
cd /opt/scan_monitor
```
Set the permissions, then run install.sh:
```
sudo chmod 755 ./install.sh
sudo ./install.sh 
```
## Usage
Enable and start the service with systemctl.
```
sudo systemctl enable scan_monitor
sudo systemctl start scan_monitor
```

Include the following at the end of a scan description to enable notifications for the scan.


## Diagnostics
Confirm the service is running. 
```commandline
systemctl status scan_monitor
```
Start the service manually (see Usage). If you are not able to start the service, run journalctl to see any errors logged by systemd. 
```commandline
sudo /bin/journalctl -u scan_monitor
```
Check /opt/scan_monitor/scan_monitor.log for errors.
```commandline
sudo tail /opt/scan_monitor/scan_monitor.log 
```
