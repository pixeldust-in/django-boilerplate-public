#!/usr/bin/env python
"""
Usage: DOPPLER_TOKEN=<token> ./bin/generate_variables.py <environment> <app_name>
"""

import logging
import os
import sys

import psycopg2
from dotenv import dotenv_values
from psycopg2 import sql
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from utils import get_doppler_envs, get_env_file_path

logger = logging.getLogger(__name__)


DOPPLER_TOKEN = os.environ.get("DOPPLER_TOKEN", None)

if not DOPPLER_TOKEN or len(sys.argv) != 2:
    print(
        """
    Please pass valid arguents as
    DOPPLER_TOKEN=<token> ./bin/create_database.py <environment>
    e.g. ./bin/create_database.py prod/dev
    """
    )
    sys.exit(0)


deploy_env = sys.argv[1]

if deploy_env not in ["dev", "prod"]:
    print("Please pass either dev or prod as the first argument")
    sys.exit(0)


doppler_envs = get_doppler_envs(
    DOPPLER_TOKEN,
    deploy_env,
    ["DB_HOST", "DB_PORT", "DB_ROOT_USER", "DB_ROOT_PASSWORD"],
)
local_envs = dotenv_values(get_env_file_path(deploy_env))

envs = {**doppler_envs, **local_envs}

DB_HOST = envs["DB_HOST"]
DB_PORT = envs["DB_PORT"]
DB_ROOT_USER = envs["DB_ROOT_USER"]
DB_ROOT_USER_WITHOUT_HOST = DB_ROOT_USER.split("@")[0]
DB_ROOT_PASSWORD = envs["DB_ROOT_PASSWORD"]
APP_DB_NAME = envs["POSTGRES_DB"]
APP_DB_USERNAME_WITH_HOST = envs["POSTGRES_USER"]
APP_DB_USERNAME = APP_DB_USERNAME_WITH_HOST.split("@")[0]
APP_DB_PASSWORD = envs["POSTGRES_PASSWORD"]


try:
    conn = psycopg2.connect(
        database="postgres",
        user=DB_ROOT_USER,
        host=DB_HOST,
        port=DB_PORT,
        password=DB_ROOT_PASSWORD,
    )
    cur = conn.cursor()
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

    print(f"🚀 Creating Role & Database for {APP_DB_NAME} in {deploy_env} environment")

    queries = [
        sql.SQL("CREATE USER {0} WITH PASSWORD {1}").format(
            sql.Identifier(APP_DB_USERNAME),
            sql.Literal(APP_DB_PASSWORD),
        ),
        sql.SQL("ALTER ROLE {0} SET client_encoding TO {1};").format(
            sql.Identifier(APP_DB_USERNAME),
            sql.Literal("utf8"),
        ),
        sql.SQL(
            "ALTER ROLE {0} SET default_transaction_isolation TO 'read committed';"
        ).format(sql.Identifier(APP_DB_USERNAME)),
        sql.SQL(f"ALTER ROLE {APP_DB_USERNAME} SET timezone TO 'UTC'"),
        sql.SQL("GRANT {0} to {1};").format(
            sql.Identifier(APP_DB_USERNAME),
            sql.Identifier(DB_ROOT_USER_WITHOUT_HOST),
        ),
        sql.SQL("CREATE DATABASE {0} WITH ENCODING='UTF8' OWNER={1}").format(
            sql.Identifier(APP_DB_NAME),
            sql.Literal(APP_DB_USERNAME),
        ),
    ]

    for query in queries:
        cur.execute(query.as_string(conn))
    print("✅ Role & Database Created!")

    conn.close()

    conn = psycopg2.connect(
        database=APP_DB_NAME,
        user=DB_ROOT_USER,
        host=DB_HOST,
        port=DB_PORT,
        password=DB_ROOT_PASSWORD,
    )
    cur = conn.cursor()
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto;")
    print("✅ Extension pgcrypto created")
    conn.close()

except Exception as error:
    logger.exception("❌ Oops! An exception has occured:", error)
    logger.exception("❌ Exception TYPE:", type(error))


print(
    f"🛫 Testing connection to the >> {APP_DB_NAME} << database for >> {APP_DB_USERNAME} << user"
)

try:
    conn = psycopg2.connect(
        database=APP_DB_NAME,
        user=APP_DB_USERNAME_WITH_HOST,
        host=DB_HOST,
        port=DB_PORT,
        password=APP_DB_PASSWORD,
    )
    cur = conn.cursor()
    cur.execute("SELECT 1")
    print(
        f"✅ Connection working for >> {APP_DB_NAME} << database for  >> {APP_DB_USERNAME} << user"
    )
    conn.close()
except Exception as error:
    logger.exception(
        "❌ Failed to connect to >> {APP_DB_NAME} << database for user {APP_DB_USERNAME}",
        error,
    )
    logger.exception("❌ Exception TYPE:", type(error))
