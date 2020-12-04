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

#### Step One: Create an account on Tenable.sc, generate API keys
1. Ensure API Keys are enabled

    - Login as admin
    
    - Go to (System / Configuration / Security)
    
    - Check the box for 'Allow API keys'
    
2. Create a new role with no permissions enabled 

    - Login as Security Manager 

    - Go to (Users / Roles)
    
    - Click on Add Role
    
    - Turn off all of the permissions
    
    - Name the role, i.e. "Monitor"
    
3. Create an account limited to the restricted role

    - As Security Manager
    
    - Go to (Users)
    
    - Click on Add User
    
    - In the Membership Section, select the Full Access Group and the new Role
    
    - Save the user
    
4. Generate API Keys for the user

    - As Security Manager
    
    - Go to (Users)
    
    - Click the Gear on right side of the user list
    
    - Select Generate API Keys

#### Step Two: Install and configure scan_monitor 
Clone the scan_monitor repository and run the install script:
```
git clone https://github.com/agroome/scan_monitor 
sudo ./scan_monitor/install.sh
```

Edit /opt/scan_monitor/etc/config.json
```javascript
{
    "access_key": "5fd58650...",
    "secret_key": "4f4a1866...",
    "sc_host": "192.168.10.10",
    "sc_port": 443,
    "poll_interval": 15,
    "smtp_server": "192.168.10.20",
    "smtp_port": 25,
    "from_address": "scanman@example.com"
}
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

