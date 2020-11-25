# scan_monitor

Monitor and report on the status of Tenable.sc scanso

*** This tool is not an officially supported Tenable project.                   
*** Use of this tool is subject to the terms and conditions identified below,  
*** and is not subject to any license agreement you may have with Tenable 

## Installation

Clone the repository into /opt/scan_monitor
```shell script
$ sudo git clone https://github.com/agroome/scan_monitor /opt/scan_monitor
$ cd /opt/scan_monitor
```
Paste your API_KEYs into the documented location in install.sh. The run install.sh with the following commands.
```shell script
$ sudo chmod 755 ./install.sh
$ sudo ./install.sh 
```

Start the service with systemctl.
```shell script
$ sudo systemctl start scan_monitor

```

Include the following at the end of a scan description to enable notifications for the scan.


```shell script
-------- do not delete this line and below --------

[notifications]

email: 
user1@example.com, user2@example.com, user3@example.com 

```

