#!/usr/bin/env python

# This script checks if host name is present in cache by first argument as key name.
# It then checks if celery is still active on that host, if yes it exits with error
# else it sets the key with hostname as value and exits successfully.
# USAGE ./bin/checknset.py safalta-celery-host


import logging
import os
import socket
import subprocess  # nosec
import sys
import time
from random import uniform

import redis

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")

import logging  # noqa

import settings  # noqa

logger = logging.getLogger(__name__)


if __name__ == "__main__":
    key_name = sys.argv[1]

    sleep_time = round(uniform(0, 30), 1)  # nosec
    logger.info(f"Sleeping for {sleep_time} seconds to avoid clashing")
    time.sleep(sleep_time)

    cache = redis.StrictRedis(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        db=settings.REDIS_CACHE_STORE,
        password=settings.REDIS_PASSWORD,
        ssl=settings.REDIS_URL_SCHEME == "rediss",
    )

    run_value = cache.get(key_name)
    if run_value:
        logger.info(
            f"Found {key_name} key with {run_value}. Searching if celery is running on host."
        )
        result = subprocess.run(  # nosec
            ["celery", "-A", "src", "inspect", "active"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            check=False,
        )
        if run_value.decode("utf8") in result.stdout:
            logger.info(f"Celery is already running on host {run_value}")
            sys.exit(1)
        logger.info("No such host found.")

    key_value = socket.gethostname()
    cache.set(key_name, key_value)
    logger.info(f"Key name: {key_name} set with value {key_value}.")
