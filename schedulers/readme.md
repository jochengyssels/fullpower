# Full Power Schedulers

This directory contains scheduler scripts for the Full Power kitesurfing application.

## Components

- `weather_scheduler.py`: Scheduler that runs the weather service periodically

## Weather Scheduler

The weather scheduler runs the weather service at regular intervals to keep the weather data up-to-date in the database.

### How It Works

1. The scheduler runs the weather service immediately when started
2. It then schedules the service to run every hour
3. The weather service fetches and stores weather data for all kitespots

## Running the Scheduler

\`\`\`bash
python schedulers/weather_scheduler.py
\`\`\`

### As a Background Process

\`\`\`bash
./start_weather_service.sh
\`\`\`

To stop the service:

\`\`\`bash
./stop_weather_service.sh
\`\`\`

## Logs

When running as a background process, logs are written to `weather_service.log` in the project root directory.

## Dependencies

- schedule
- services.weather_service
\`\`\`

\`\`\`

Let's also update the start_weather_service.sh script to use the new scheduler location:
