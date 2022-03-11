#!/bin/bash
for pid in $(pgrep -f main.py); do
    if [ $pid != $$ ]; then
        exit 1
    fi 
done

source env/bin/activate;

python3 catTelemetry.py