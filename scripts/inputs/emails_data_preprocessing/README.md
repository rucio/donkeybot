THE COLUMNS NEEDS TO BE EDITED IN EVERY SCRIPT, TODO: make configurable
NOT PY2 compatible

# create_sqlite_tables.py
creates emails db and table.
execute with python3 create_sqlite_tables.py
columns: sender, receiver, subject, date, thread, body

# update_db.py
module for updating row in the db
not executalbe

# read_db.py
script for getting a row in db
edit it and
execute: python3 read_db.py

# fetch_emails.py
the main script to fetch emails and call update_db module. Insert a login and pasw.
execute: python3 fetch_emails.py

# __init__.py
empty, for modules

# procedure from scratch:
- remove db/emails.db and __pycache__ if present
- python3 create_sqlite_tables.py
- edit pasw and login in fetch_emails.py
- python3 fetch_emails.py
- python3 read_db.py
