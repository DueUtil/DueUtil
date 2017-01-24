#!/bin/sh
until python3 dueutil.py; do
    echo "Script 'dueutil.py' crashed with exit code $?.  Respawning.." >&2
    sleep 1
done
