#!/bin/bash

# debug server to send test messages 

python3 -m smtpd -c DebuggingServer -n localhost:25

