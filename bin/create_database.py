#!/usr/bin/env python

import logging
import os

import psycopg2
from psycopg2 import sql

logger = logging.getLogger(__name__)

DB_HOST = os.environ.get("DB_HOST")
DB_PORT = os.environ.get("DB_PORT")
DB_ROOT_USER = os.environ.get("DB_ROOT_USER")
DB_ROOT_PASSWORD = os.environ.get("DB_ROOT_PASSWORD")

APP_DB_NAME = os.environ.get("POSTGRES_DB")
APP_DB_USERNAME = os.environ.get("POSTGRES_USER").split("@")[0]
APP_DB_PASSWORD = os.environ.get("POSTGRES_PASSWORD")

try:
    conn = psycopg2.connect(
        database="postgres",
        user=DB_ROOT_USER,
        host=DB_HOST,
        port=DB_PORT,
        password=DB_ROOT_PASSWORD,
    )
    cur = conn.cursor()
    cur.execute(
        "SELECT rolname FROM pg_catalog.pg_roles"
    )  # WHERE rolname = %s", [username])
    query = sql.SQL("CREATE USER {0} LOGIN PASSWORD {1}").format(
        sql.Identifier(APP_DB_USERNAME),
        sql.Literal(APP_DB_PASSWORD),
    )
    cur = conn.cursor()
    cur.execute(query.as_string(conn))
    cur.execute("COMMIT")
except Exception as error:
    logger.exception("Oops! An exception has occured:", error)
    logger.exception("Exception TYPE:", type(error))


# TODO: Remove root variables from env after completion of this script