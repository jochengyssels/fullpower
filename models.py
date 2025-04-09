from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey, Text, TIMESTAMP
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base


Base = declarative_base()

# Simple User model
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)



class KiteSpot(Base):
    __tablename__ = "kitespots"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(Text, nullable=True)
    latitude = Column(Float)
    longitude = Column(Float)
    country = Column(String, nullable=True)
    region = Column(String, nullable=True)  # This will store the 'location' from CSV
    city = Column(String, nullable=True)
    difficulty = Column(String, nullable=True)  # beginner, intermediate, advanced
    water_type = Column(String, nullable=True)  # waves, choppy, flat
    best_wind_direction = Column(String, nullable=True)
    best_season = Column(String, nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(TIMESTAMP(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Add relationships
    weather_data = relationship("KiteSpotWeather", back_populates="kitespot")
    favorite_by = relationship("FavoriteSpot", back_populates="kitespot")
    sessions = relationship("KiteSession", back_populates="kitespot")

class KiteSpotWeather(Base):
    __tablename__ = "kitespot_weather"

    id = Column(Integer, primary_key=True, index=True)
    kitespot_id = Column(Integer, ForeignKey("kitespots.id"))
    timestamp = Column(TIMESTAMP(timezone=True), index=True)
    temperature = Column(Float, nullable=True)
    humidity = Column(Float, nullable=True)
    precipitation = Column(Float, nullable=True)
    wind_speed_10m = Column(Float, nullable=True)
    wind_direction_10m = Column(Float, nullable=True)
    cloud_cover = Column(Float, nullable=True)
    visibility = Column(Float, nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), default=lambda: datetime.now(timezone.utc))

    # Add relationship to kitespot
    kitespot = relationship("KiteSpot", back_populates="weather_data")


class FavoriteSpot(Base):
    __tablename__ = "favorite_spots"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    kitespot_id = Column(Integer, ForeignKey("kitespots.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="favorite_spots")
    kitespot = relationship("KiteSpot", back_populates="favorite_by")

class KiteSession(Base):
    __tablename__ = "kite_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    kitespot_id = Column(Integer, ForeignKey("kitespots.id"))
    date = Column(DateTime(timezone=True))
    duration_minutes = Column(Integer)
    kite_size = Column(Float)
    wind_speed = Column(Float)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="sessions")
    kitespot = relationship("KiteSpot", back_populates="sessions")

class KiteSchool(Base):
    __tablename__ = "kiteschools"

    id = Column(Integer, primary_key=True, index=True)
    company_name = Column(String, index=True)
    location = Column(String)
    country = Column(String, index=True)
    google_review_score = Column(String, nullable=True)
    owner_name = Column(String, nullable=True)
    website_url = Column(String, nullable=True)
    course_pricing = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())