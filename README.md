# scan_monitor

> This tool is NOT officially supported Tenable software. Use of this tool is subject to the terms and conditions 
> identified in the [LICENSE](LICENSE),  and is not subject to any license agreement you may have with Tenable.

## Overview
Monitor and report on the status of Tenable.sc scans. 

scan_monitor polls the Tenable.sc API to provide enhanced email notification capabilities. 

## Capabilities

- Send email notification when a scan instance changes into one of the following states: 
  - 'Running': A scan has started running
  - 'Paused': A scan has paused 
  - 'Completed': A scan has completed
  - 'Partial': A scan has completed with partial results
  - 'Error': An error has completing or importing the scan
 
- Define email distribution in the form of metadata appended to the scan definition.

- Create custom messages using Jinja templates and metadata associated with the scan

## Requirements 
 - Python 3.6+
 - Install script for Ubuntu, follow along for other OS
 - requires python3-venv and python3-systemd

## Getting Started
### Installation 
Follow the steps below to generate API keys for a least privileged account on Tenable.sc.
- [Ensure API Keys Are Enabled](#ensure-api-keys-are-enabled)

- [Create a Restricted Role](#create-a-restricted-role)

- [Create an Account with the Restricted Role](#create-an-account-with-the-restricted-role)

- [Generate API Keys](#create-tenablesc-account-and-api-keys)

On another system that is sufficiently secured

- [Install and configure scan_monitor](#install-and-configure-scan_monitor)

### Usage and customization

- [Configure email notifications](#configure-email-notifications)

- [Customize email template](#configure-email-notifications)


## Ensure Api Keys are Enabled
Complete this step as the Admin user

- Go to (System / Configuration / Security)
    
- Check the box for 'Allow API keys'
## Create a restricted role 
Switch to an account with Security Manager privileges for the following steps
- Go to (Users / Roles)
    
- Click on Add Role
    
- Name the role, i.e. "Monitor"
    
- Turn off all of the permissions, ensure all boxes are unchecked
    
- Click Submit
## Create an account with the restricted role

- Go to (Users)
    
- Click on Add User
    
- Add the user to:
    - Full Access Group 
        
    - The restricted role created in the previous step
    
- Click Submit
## Generate API Keys

- Go to (Users)
    
- Click the Gear on right side of the user list
    
- Select Generate API Keys
    
- Record the keys to a secure file or keep this window open for the next step

## Install and configure scan_monitor
Clone the repository, then run install.sh
```
git clone https://github.com/agroome/scan_monitor 
sudo ./scan_monitor/install.sh
```

After installing run configure
```
sudo /opt/scan_monitor/bin/configure
```

Once configured, use systemctl to start the service.
```
sudo systemctl start scan_monitor.service
```

### Configure email notifications 
Include the following at the end of a Tenable.sc scan description to enable notifications for the scan.

```
This is the description.


-------- do not delete this line and below --------      
[email notification]
to: agroome@tenable.com
subject: {{ name }}: {{ status }}
```

### Customize notification template
The following scan instance variables can be used in the notification templates. 
Templates are located in /opt/scan_monitor/templates.
```
instance_variables = [
    'id', 'name', 'description', 'status', 'initiator', 'owner', 'ownerGroup',
    'repository', 'scan', 'job', 'details', 'importStatus', 'importStart', 'importFinish',
    'initiator', 'owner', 'ownerGroup', 'repository', 'scan', 'job', 'details', 'importStatus',
    'importStart', 'importFinish', 'importDuration', 'downloadAvailable', 'resultType', 'resultSource',
    'running', 'errorDetails', 'importErrorDetails', 'totalIPs', 'scannedIPs', 'startTime', 'finishTime',
    'scanDuration, completedIPs', 'completedChecks', 'totalChecks', 'agentScanUUID', 'agentScanContainerUUID',
]
```

Default template using some of the variables:
```
{{ name }}
details: {{ details }}

Targets:
    scanned IPs: {{ scannedIPs }}
    total IPs:   {{ totalIPs }}

Checks:
    completed:  {{ completedChecks }}
    total:      {{ totalChecks }}

Scan {{ status }}.
{%- if status != 'Completed' %}
    {{ errorDetails }}
{% endif %}
Import {{ importStatus }}.
{%- if importStatus != 'Completed' %}
    {{ importErrorDetails }}
{% endif %}
```
The following is example of output using the above template. The license happened to expire during the scan resulting 
in a completed (Partial) scan which was blocked on import due to the expired license. This was all reflected in the 
notification.
```
RTP Office - Discovery
details: Discovery scan designed to test a roll-over scan.

Targets:
    scanned IPs: 1
    total IPs:   256

Checks:
    completed:  123804
    total:      31693824

Scan Partial.
    The Scan was stopped, partial results imported, and a rollover Scan template created for the remaining IPs.

Import Blocked.
    Scan import error. License invalid: status 65.
```

Read about Jinja templates here: [Jinja2 docs](https://jinja2docs.readthedocs.io/)

### Files
 - /opt/scan_monitor/var/log/notify.log
 - /opt/scan_monitor/.monitor_env

### License
The project is licensed under the MIT license.



