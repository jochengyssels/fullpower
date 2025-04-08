#!/bin/bash

# Create systemd service file
cat > /tmp/kitespot-weather.service << EOL
[Unit]
Description=Kitespot Weather Service
After=network.target

[Service]
User=$(whoami)
WorkingDirectory=$(pwd)
ExecStart=$(which python) weather_scheduler.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOL

# Move service file to systemd directory
sudo mv /tmp/kitespot-weather.service /etc/systemd/system/

# Reload systemd, enable and start the service
sudo systemctl daemon-reload
sudo systemctl enable kitespot-weather
sudo systemctl start kitespot-weather

echo "Weather service installed and started"
echo "Check status with: sudo systemctl status kitespot-weather"