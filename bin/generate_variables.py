#!/usr/bin/env python
"""
Usage: DOPPLER_TOKEN=<token> ./bin/generate_variables.py <environment> <app_name>
"""

import logging
import os
import secrets
import sys
from pathlib import Path

import requests

logger = logging.getLogger(__name__)

DOPPLER_TOKEN = os.environ.get("DOPPLER_TOKEN", None)

if not DOPPLER_TOKEN or len(sys.argv) != 3:
    print(
        """
    Please pass valid arguents as
     DOPPLER_TOKEN=<token> ./bin/generate_variables.py <environment> <app_name>
    e.g. ./bin/generate_variables.py prod/dev safalta
    """
    )
    sys.exit(0)


deploy_env = sys.argv[1]
app_name = sys.argv[2]


if deploy_env not in ["dev", "prod"]:
    print("Please pass either dev or prod as the first argument")
    sys.exit(0)

if "pgtry" in app_name or "pg" in app_name:
    print("Please remove pgtry or pg from the app name")
    sys.exit(0)


def get_doppler_envs():
    url = f"https://api.doppler.com/v3/configs/config/secrets?project=pgtry&config={deploy_env}&include_dynamic_secrets=false"
    headers = {"accept": "application/json", "authorization": f"Bearer {DOPPLER_TOKEN}"}

    response = requests.get(url, headers=headers, timeout=10)
    if response.status_code != 200:
        logger.exception(
            "Error fetching secrets from doppler - Response >>> %s", response.text
        )
        sys.exit(0)
    else:
        secrets = response.json()["secrets"]
        secrets = {k: v["raw"] for k, v in secrets.items() if v["raw"] != ""}
        return secrets


# initializing size of string
RANDOM_STRING_CHARS = (
    "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!@#&*()"
)


def get_random_string(length, allowed_chars=RANDOM_STRING_CHARS):
    return "".join(secrets.choice(allowed_chars) for i in range(length))


ENVS = get_doppler_envs()


CONFIG = {
    # Misc
    "COMPOSE_NAME": app_name,
    "LOG_LEVEL": "INFO",
    "ALLOWED_HOSTS": "*",
    "ALLOWED_ORIGINAL_HOST": ["*", "localhost"],
    "EMAIL_FROM_EMAIL": "info@pgtry.com",
    "EMAIL_FROM_NAME": f"P&G {app_name.capitalize()}",
    "APP_SECRET_KEY": get_random_string(40),
    "PGCRYPTO_KEY": get_random_string(9),
    # VFirst
    "VF_EMAIL_ENDPOINT": ENVS["VF_EMAIL_ENDPOINT"],
    "VF_EMAIL_USERNAME": ENVS["VF_EMAIL_USERNAME"],
    "VF_EMAIL_PASSWORD": ENVS["VF_EMAIL_PASSWORD"],
    "VFIRST_SMS_API_URL": ENVS["VFIRST_SMS_API_URL"],
    "VFIRST_SMS_API_KEY": ENVS["VFIRST_SMS_API_KEY"],
    # Infra
    "DB_HOST": ENVS["DB_HOST"],
    "POSTGRES_USER": f"{app_name}{ENVS['POSTGRES_USER']}",
    "POSTGRES_DB": f"{app_name}",
    "POSTGRES_PASSWORD": get_random_string(15),
    "DB_PORT": "5432",
    "REDIS_CACHE_STORE": "0",
    "REDIS_HOST": ENVS["REDIS_HOST"],
    "REDIS_PASSWORD": ENVS["REDIS_PASSWORD"],
    "REDIS_PORT": "6380",
    "REDIS_URL_SCHEME": "rediss",
    "DOCKER_REGISTRY_SERVER_URL": ENVS["DOCKER_REGISTRY_SERVER_URL"],
    "DOCKER_REGISTRY_SERVER_USERNAME": ENVS["DOCKER_REGISTRY_SERVER_USERNAME"],
    "DOCKER_REGISTRY_SERVER_PASSWORD": ENVS["DOCKER_REGISTRY_SERVER_PASSWORD"],
    "DOCKER_CUSTOM_IMAGE_NAME": f"{ENVS['DOCKER_CUSTOM_IMAGE_NAME']}/pgtry-{app_name}:{deploy_env}",
    # Docker
    "DIAGNOSTICS_AZUREBLOBRETENTIONINDAYS": "90",
    "DOCKER_ENABLE_CI": "true",
    "WEBSITE_DNS_SERVER": "168.63.129.16",
    "WEBSITE_HTTPLOGGING_RETENTION_DAYS": 90,
    "WEBSITE_VNET_ROUTE_ALL": 1,
    "WEBSITES_ENABLE_APP_SERVICE_STORAGE": "false",
    "WEBSITE_HTTPLOGGING_CONTAINER_URL": "https://logextconsumerap01.blob.core.windows.net/az-ap-cs-webapp-log?sp=rwl&st=2019-02-06T12:43:59Z&se=2029-02-28T12:43:00Z&sv=2018-03-28&sig=rnwOPc3cx8466GSiAwaAr0BSHnrNKp1NvNAdjgbitjA%3D&sr=c",  # noqa
    "DIAGNOSTICS_AZUREBLOBCONTAINERSASURL": "https://logextconsumerap01.blob.core.windows.net/az-ap-cs-webapp-log?sp=rwl&st=2019-02-06T12:43:59Z&se=2029-02-28T12:43:00Z&sv=2018-03-28&sig=rnwOPc3cx8466GSiAwaAr0BSHnrNKp1NvNAdjgbitjA%3D&sr=c",  # noqa
}


def is_value_a_fuction(val):
    return hasattr(val, "__call__")


def format_value(val):
    if isinstance(val, list):
        return ",".join(val)
    if is_value_a_fuction(val):
        return val()
    return val


def write_env_file():
    file_name = Path(f"deploy/docker/{deploy_env}/.env")
    with open(file_name, "a", encoding="utf-8") as file:
        for key, value in CONFIG.items():
            file.write(
                f'{key}="{format_value(value)}"\n',
            )


if __name__ == "__main__":
    write_env_file()
