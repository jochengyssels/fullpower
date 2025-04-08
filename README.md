# Kitespot Weather Application

A full-stack application for kitesurfers to track weather conditions, manage favorite spots, and log sessions. The application provides real-time weather data for kitesurfing spots worldwide, with a focus on wind conditions and optimal kitesurfing windows.

## Features

- 🌍 Global kitespot database with detailed information
- 🌤️ Real-time weather data for each kitespot
- 💨 Wind condition tracking and forecasting
- 📊 Golden window calculation for optimal kitesurfing conditions
- 👤 User profiles with favorite spots
- 📝 Session logging
- 🏫 Kiteschool directory
- 🔄 Automatic weather data updates

## Tech Stack

### Backend
- Python 3.12+
- FastAPI
- SQLAlchemy
- PostgreSQL
- Open-Meteo API for weather data
- LocationIQ API for geocoding

### Frontend (To be implemented)
- React/Next.js
- TypeScript
- Tailwind CSS

## Prerequisites

- Python 3.12 or higher
- PostgreSQL 12 or higher
- Node.js 18 or higher (for frontend)
- Virtual environment (recommended)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/kitespot-weather.git
cd kitespot-weather
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install Python dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
Create a `.env` file in the root directory with the following variables:
```env
# Backend environment variables
DATABASE_URL=postgresql+asyncpg://username:password@localhost/kitesurf
TOMORROW_API_KEY=your_tomorrow_api_key
LOCATIONIQ_API_KEY=your_locationiq_api_key

# Frontend environment variables
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000  # Backend API URL
```

5. Initialize the database:
```bash
python update_schema.py
```

6. Import initial kitespot data:
```bash
python reset_and_import_kitespots.py
```

## Running the Application

### Backend

1. Start the API server:
```bash
uvicorn main:app --reload
```
The API will be available at `http://localhost:8000`

2. Start the weather service (in a separate terminal):
```bash
python services/weather_service.py
```

### API Documentation

Once the server is running, you can access:
- Swagger UI documentation: `http://localhost:8000/docs`
- ReDoc documentation: `http://localhost:8000/redoc`

## API Endpoints

### Kitespots
- `GET /api/kitespots/` - List all kitespots
- `GET /api/kitespots/{id}` - Get kitespot details
- `GET /api/kitespots/{id}/weather` - Get weather data for a kitespot

### Weather
- `GET /api/weather` - Get weather forecast for a location

### Users
- `POST /api/users/` - Create a new user
- `GET /api/users/{id}/favorites` - Get user's favorite spots
- `POST /api/users/{id}/favorites` - Add a favorite spot
- `GET /api/users/{id}/sessions` - Get user's sessions
- `POST /api/users/{id}/sessions` - Log a new session

### Kiteschools
- `GET /api/kiteschools` - List kiteschools

## Database Schema

### KiteSpot
- id (Primary Key)
- name
- description
- latitude
- longitude
- country
- region
- city
- difficulty
- water_type
- best_wind_direction
- best_season
- created_at
- updated_at

### KiteSpotWeather
- id (Primary Key)
- kitespot_id (Foreign Key)
- timestamp
- temperature
- humidity
- precipitation
- wind_speed_10m
- wind_direction_10m
- cloud_cover
- visibility
- created_at

### User
- id (Primary Key)
- email
- hashed_password
- is_active
- is_superuser
- created_at
- updated_at

### FavoriteSpot
- id (Primary Key)
- user_id (Foreign Key)
- kitespot_id (Foreign Key)
- created_at

### KiteSession
- id (Primary Key)
- user_id (Foreign Key)
- kitespot_id (Foreign Key)
- date
- duration_minutes
- kite_size
- wind_speed
- notes
- created_at

### KiteSchool
- id (Primary Key)
- company_name
- location
- country
- google_review_score
- owner_name
- website_url
- course_pricing
- created_at

## Development

### Code Structure
```
.
├── main.py              # FastAPI application entry point
├── models.py            # SQLAlchemy models
├── schemas.py           # Pydantic schemas
├── crud.py             # Database operations
├── database.py         # Database configuration
├── services/           # Service modules
│   ├── weather_service.py
│   └── geocoding.py
├── data/               # Data files
│   └── kitespots.csv
└── tests/              # Test files
```

### Adding New Features

1. Create new models in `models.py`
2. Define Pydantic schemas in `schemas.py`
3. Implement CRUD operations in `crud.py`
4. Add new endpoints in `main.py`
5. Update the database schema using `update_schema.py`

### Testing

Run tests using pytest:
```bash
pytest
```

## Deployment

### Backend Deployment

1. Set up a PostgreSQL database
2. Configure environment variables
3. Run database migrations
4. Deploy using a process manager (e.g., PM2, Supervisor)
5. Set up a reverse proxy (e.g., Nginx)

### Frontend Deployment

1. Build the frontend application
2. Deploy to a static hosting service or CDN
3. Configure environment variables
4. Set up CI/CD pipeline

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Open-Meteo for weather data
- LocationIQ for geocoding services
- All contributors and users of the application

