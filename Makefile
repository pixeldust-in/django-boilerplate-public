.PHONY: all help run collect deps migrate freeze
FILENAME := .appname
APPNAME := `cat $(FILENAME)`

# target: all - Runs both django and celery if used with -j
all: run yarn

# target: help - Display callable targets.
help:
	@egrep "^# target:" [Mm]akefile

# target: run - Runs a dev server on localhost:8000
run:
	manage runserver

# target: deps - install dependencies from requirements file
prod_deps:
	pip install -r requirements.txt
	cd src && pip install -e .
	# make frontend_build

dev_deps:
	pip install -U pip setuptools
	pip install -r dev-requirements.txt

deps: dev_deps prod_deps


# target: migrate - migrate the database
migrate:
	manage migrate

# target: sh - open django extension's shell plus
sh:
	manage shell_plus

# target: db - open django DB shell
db:
	manage dbshell


# target: run tailwind css server in dev mode
# frontend_build:
	# cd app && yarn && yarn build

# target: edit - Decrypt and edit ansible secrets file
update_env_secrets:
	export EDITOR='code -w' && ansible-vault edit deploy/group_vars/dev.yml
