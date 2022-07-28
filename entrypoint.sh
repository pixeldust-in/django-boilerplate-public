#!/bin/bash

set -e
set -m

sed -i "s/SSH_PORT/$SSH_PORT/g" /etc/ssh/sshd_config
service ssh start

# Get environment variables to show up in SSH session
eval $(printenv | sed -n "s/^\([^=]\+\)=\(.*\)$/export \1=\2/p" | sed 's/"/\\\"/g' | sed '/=/s//="/' | sed 's/$/"/' >> /etc/profile)

gunicorn -c src/gunicorn.py src.wsgi &

log_level=$(echo $LOG_LEVEL | echo info)
echo "LOG_LEVEL is set at $log_level"
fg


#NOTE: Uncomment below code only if celery is needed in your app

# set +e # Next statement is expected to fail so we temporarily disable error exit
# ./bin/checknset.py oralb-cic-celery-host
# IS_CELERY_RUNNING=$?
# set -e
# if [[ $IS_CELERY_RUNNING -eq "0" ]]; then
#     echo No existing celery found. Running celery now
#     celery -A src worker -l $log_level --concurrency=1 &
#     celery -A src beat --scheduler django_celery_beat.schedulers:DatabaseScheduler -l $log_level
# else
#     echo "Celery already running. Skipping running another celery command."
#     fg
# fi