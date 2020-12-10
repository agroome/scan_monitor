# scan_monitor

Monitor and report on the status of Tenable.sc scans. 

scan_monitor polls the Tenable.sc API and sends an email notification
to a defined list of users when a scan instance changes into one of the following states: 
 - 'Running': A scan has started running
 - 'Paused': A scan has paused 
 - 'Completed': A scan has completed
 - 'Partial': A scan has completed with partial results
 - 'Error': An error has completing or importing the scan
 

> This tool is NOT officially supported Tenable software. Use of this tool is subject to the terms and conditions 
> identified in the [LICENSE](LICENSE),  and is not subject to any license agreement you may have with Tenable.

## Getting Started

[Enable API keys on Tenable.sc](#enable-api-keys-on-tenablesc)

[Create a service account](#create-a-service-account)

[Generate API Keys](#generate-api-keys)

[Install and configure scan_monitor](#install-and-configure-scan_monitor)

[Configure email notifications](#configure-email-notifications)


#### Enable API keys on Tenable.sc

Complete this step as the Admin user.

- Ensure API Keys are enabled

    - Go to (System / Configuration / Security)
    
    - Check the box for 'Allow API keys'
   
#### Create a service account
Switch to an account with Security Manager privileges for the next steps.

- Create a new role with no permissions enabled 

    - Go to (Users / Roles)
    
    - Click on Add Role
    
    - Name the role, i.e. "Monitor"
    
    - Turn off all of the permissions, ensure all boxes are unchecked
    
    - Click Submit
    
- Create an account limited to the restricted role

    - Go to (Users)
    
    - Click on Add User
    
    - Add the 
        - Full Access Group 
        
        - The role created in step (2)
    
    - Click Submit
    
    
#### Generate API Keys
Also using a Security Manager account.
 - Go to (Users)
    
 - Click the Gear on right side of the user list
    
 - Select Generate API Keys
    
 - Record the keys to a secure file or keep this window open for the next step

#### Install and configure scan_monitor
Clone the repository, then run install.sh
```
git clone https://github.com/agroome/scan_monitor 
sudo ./scan_monitor/install.sh
```

Edit /opt/scan_monitor/etc/config.json (poll_interval in seconds)
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

#### Start the scan_monitor service
Control the service with systemctl. For example:
```
sudo systemctl start scan_monitor.service
```

#### Configure email notifications 
Include the following at the end of a Tenable.sc scan description to enable notifications for the scan.

```
--- do not delete below this line ---
[notifications]
email: user1@example.com, user2@example.com, user3@example.com 
```

#### File locations
 - /opt/scan_monitor/var/log/notify.log
 - /opt/scan_monitor/etc/config.json


