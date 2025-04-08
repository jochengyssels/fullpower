
# Full Power - Kitesurfing Weather Application

## Overview

Full Power is a comprehensive kitesurfing application that provides real-time weather data, forecasts, and "golden kite window" calculations to help kitesurfers find the best time and location for their sessions.

## System Architecture

The application consists of several components:

1. **FastAPI Backend**: Provides RESTful API endpoints for kitespots, weather data, and user management
2. **PostgreSQL Database**: Stores kitespot information, user data, and weather forecasts
3. **Weather Service**: Fetches and processes weather data from Open-Meteo API
4. **Frontend**: (To be implemented) User interface for accessing the application

## Setup Instructions

### Prerequisites

- Python 3.10+
- PostgreSQL
- Virtual environment (recommended)

### Installation

1. Clone the repository:
   \`\`\`bash
   git clone https://github.com/yourusername/fullpower.git
   cd fullpower
   \`\`\`

2. Create and activate a virtual environment:
   \`\`\`bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   \`\`\`

3. Install dependencies:
   \`\`\`bash
   pip install -r requirements.txt
   \`\`\`

4. Set up the database:
   \`\`\`bash
   # Create a PostgreSQL database
   createdb fullpower
   
   # Update the DATABASE_URL in database.py if needed
   
   # Initialize the database schema
   python update_schema.py
   
   # Seed the database with initial data (if available)
   python seed_db.py
   \`\`\`

5. Start the FastAPI server:
   \`\`\`bash
   python main.py
   \`\`\`

6. Start the weather service:
   \`\`\`bash
   python services/weather_scheduler.py
   \`\`\`

### Environment Variables

Create a `.env` file in the root directory with the following variables:

\`\`\`
DATABASE_URL=postgresql+asyncpg://username:password@localhost/fullpower
LOCATIONIQ_API_KEY=your_locationiq_api_key
SECRET_KEY=your_secret_key_for_jwt
\`\`\`

## API Documentation

Once the server is running, you can access the API documentation at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Main Endpoints

- `/api/kitespots`: CRUD operations for kitespots
- `/api/kitespots/{kitespot_id}/weather`: Get weather data for a specific kitespot
- `/api/weather`: Get weather data and golden kite window for a location
- `/api/users`: User management endpoints

## Weather Service

The weather service fetches and stores hourly weather data for all kitespots in the database. It runs as a separate process and updates the data every hour.

### Running the Weather Service

\`\`\`bash
# Run directly
python services/weather_scheduler.py

# Or use the start script
./start_weather_service.sh
\`\`\`

### Weather Data Sources

The application uses the Open-Meteo API to fetch weather data. The data includes:
- Temperature
- Humidity
- Precipitation
- Wind speed at different heights (10m, 80m, 120m)
- Wind direction
- Wind gusts

## Database Schema

### Main Tables

1. **users**: User account information
2. **kitespots**: Information about kitesurfing locations
3. **kitespot_weather**: Hourly weather data for each kitespot

### Updating the Schema

If you make changes to the models, run the update_schema.py script to apply the changes to the database:

\`\`\`bash
python update_schema.py
\`\`\`

## Troubleshooting

### Common Issues

1. **Database connection errors**:
   - Check that PostgreSQL is running
   - Verify the DATABASE_URL in database.py or .env file
   - Ensure the database exists and the user has proper permissions

2. **API key errors**:
   - Verify that all required API keys are set in the .env file
   - Check for API usage limits

3. **Import errors**:
   - Ensure all dependencies are installed
   - Check that you're running commands from the project root directory

### Logs

- Application logs are written to the console by default
- Weather service logs are written to weather_service.log when running in the background

## Development Guidelines

### Adding New Features

1. Create a new branch for your feature
2. Implement the feature with appropriate tests
3. Update the README.md if necessary
4. Submit a pull request

### Code Style

- Follow PEP 8 guidelines for Python code
- Use async/await for database operations and external API calls
- Document all functions and classes with docstrings

## Scripts

### start_backend.sh

Starts the FastAPI backend server:

\`\`\`bash
#!/bin/bash
source venv/bin/activate
python main.py
\`\`\`

### start_weather_service.sh

Starts the weather service in the background:

\`\`\`bash
#!/bin/bash
source venv/bin/activate
python services/weather_scheduler.py > weather_service.log 2>&1 &
echo $! > weather_service.pid
\`\`\`

### stop_weather_service.sh

Stops the weather service:

\`\`\`bash
#!/bin/bash
if [ -f weather_service.pid ]; then
    kill $(cat weather_service.pid)
    rm weather_service.pid
fi
\`\`\`

## License

[Your license information here]

## Contact

[Your contact information here]
\`\`\`

Let's also create a specific README for the weather service:
