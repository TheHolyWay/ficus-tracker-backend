#!/usr/bin/env bash

flask db init
flask db migrate
flask db upgrade

python /opt/ficus-tracker/ficus_tracker.py