#!/bin/sh
until python3 DueUtil.py; do
    echo "Script 'DueUtil.py' crashed with exit code $?.  Respawning.." >&2
    sleep 1
done