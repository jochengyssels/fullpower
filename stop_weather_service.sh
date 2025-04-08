#!/bin/bash

if [ -f weather_service.pid ]; then
    PID=$(cat weather_service.pid)
    echo "Stopping weather service (PID: $PID)..."
    kill $PID
    rm weather_service.pid
    echo "Weather service stopped"
else
    echo "Weather service is not running"
fi
