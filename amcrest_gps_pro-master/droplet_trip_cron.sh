#!/bin/sh
echo "activated sccount";
python3 /root/amcrest_backend_phase2/manage.py runcrons
echo "activated sccount";


# */1 * * * * bash /root/amcrest_backend_phase2/droplet_trip_cron.sh > /root/amcrest_backend_phase2/cronjob.log