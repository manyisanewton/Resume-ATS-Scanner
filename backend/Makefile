.PHONY: install run test db-init db-migrate db-upgrade

install:
	python3 -m venv .venv
	. .venv/bin/activate && pip install --upgrade pip && pip install -r requirements.txt

run:
	. .venv/bin/activate && python run.py

test:
	. .venv/bin/activate && pytest

db-init:
	. .venv/bin/activate && flask --app run.py db init

db-migrate:
	. .venv/bin/activate && flask --app run.py db migrate -m "schema update"

db-upgrade:
	. .venv/bin/activate && flask --app run.py db upgrade
