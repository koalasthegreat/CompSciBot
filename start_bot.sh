#!/bin/bash

# Run migrations
python3 -m alembic upgrade head

# Run bot
python3 -m compscibot
