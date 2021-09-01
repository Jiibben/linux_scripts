#!/usr/bin/bash
onedrive --synchronize
echo "ran at $(date)" >> /home/allanburnier/.personal_log/onedrive_cron.log
