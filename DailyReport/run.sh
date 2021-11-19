#!/bin/bash

# Start the run once job.
echo "Start the scheduler (logging in /var/log/script.log)"

declare -p | grep -Ev 'BASHOPTS|BASH_VERSINFO|EUID|PPID|SHELLOPTS|UID' > /container.env

# Setup a cron schedule
echo "SHELL=/bin/bash
BASH_ENV=/container.env
0 9 * * * (cd /app;python /app/main.py) >> /var/log/script.log 2>&1
# Cronjob to run the reporter" > scheduler.txt

crontab scheduler.txt
cron -f