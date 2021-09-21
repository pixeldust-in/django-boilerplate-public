# Django Project

Code repository for Django-project

## Dependencies
### PostgreSQL Database
Setup database based on your OS. Please also install Postgis plugin for postgresql and postgresql-contrib package for pgcrypto. You can then create a DB as follows

Enter into postgres(superuser) user's shell
```bash
sudo -u postgres -i
```
Copy paste below commands till EOF and press enter:
```bash
export DB_NAME='project-name'
export DB_OWNER=$DB_NAME
export DB_PASSWORD=devpassword
psql <<EOF
CREATE USER $DB_OWNER WITH PASSWORD '$DB_PASSWORD';
ALTER ROLE $DB_OWNER SET client_encoding TO 'utf8';
ALTER ROLE $DB_OWNER SET default_transaction_isolation TO 'read committed';
ALTER ROLE $DB_OWNER SET timezone TO 'UTC';
CREATE DATABASE  $DB_NAME WITH ENCODING='UTF8' OWNER='$DB_OWNER';
EOF
```

FOR BACKUP AND RESTORING DATABASE
```
1. Backup
sudo su - postgres
pg_dump database_name > postgres.bak

2. Restore
sudo su - postgres
psql database_name < backup_file
```

## Installation
### On Local Machine
Run the following commands to have the server up and running.
Project based on Python 3.7.5
```bash
$ cp .env.example .env
```
And then take care of other formalities
```bash
$ python3 -m venv venv
$ source venv/bin/activate
$ make deps
$ pip install -r dev-requirements.txt
$ make build
```
Run migrations
```
$ manage migrate
```
Create a super user
```
$ manage createsuperuser
```
Execute just `make` command with no args and the django dev server should be running on `localhost:8000`

When making any changes to the code before committing please run `pre-commit install` once to apply the hooks on git commits.