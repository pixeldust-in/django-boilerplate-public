import logging
import os
import sys
from pathlib import Path

import requests

DOPPLER_TOKEN = os.environ.get("DOPPLER_TOKEN", None)
BASE_DIR = Path(__file__).resolve().parent.parent

logger = logging.getLogger(__name__)


def get_doppler_envs(doppler_token, deploy_env, required_secrets="*"):
    """
    required_secrets: list of secrets to fetch from doppler. * if all secrets required
    """
    url = f"https://api.doppler.com/v3/configs/config/secrets?project=pgtry&config={deploy_env}&include_dynamic_secrets=false"
    if required_secrets != "*" and isinstance(required_secrets, list):
        url += f"&secrets={','.join(required_secrets)}"
    headers = {"accept": "application/json", "authorization": f"Bearer {doppler_token}"}

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


def get_env_file_path(deploy_env):
    return Path(BASE_DIR, "deploy/docker/", deploy_env, f".azure-{deploy_env}.env")
