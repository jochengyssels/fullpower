#!/bin/bash

# Activate virtual environment if you're using one
source venv/bin/activate

# Start the weather service
echo "Starting weather service..."
python schedulers/weather_scheduler.py > weather_service.log 2>&1 &
echo $! > weather_service.pid
echo "Weather service started with PID $(cat weather_service.pid)"
echo "Logs are being written to weather_service.log"
