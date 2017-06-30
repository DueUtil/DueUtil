#!/bin/sh
until python3 run.py; do
    echo "Script 'run.py' crashed with exit code $?.  Respawning.." >&2
    sleep 1
done
