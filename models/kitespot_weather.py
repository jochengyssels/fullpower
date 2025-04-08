from datetime import datetime, timezone
from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey
from sqlalchemy.types import TIMESTAMP
from sqlalchemy.orm import relationship
from database import Base

class KiteSpotWeather(Base):
    __tablename__ = 'kitespot_weather'

    id = Column(Integer, primary_key=True)
    kitespot_id = Column(Integer, ForeignKey('kitespots.id'), nullable=False)
    timestamp = Column(TIMESTAMP(timezone=True), nullable=False)
    temperature = Column(Float)
    humidity = Column(Float)
    precipitation = Column(Float)
    rain = Column(Float)
    wind_speed_10m = Column(Float)
    wind_speed_80m = Column(Float)
    wind_speed_120m = Column(Float)
    wind_direction_10m = Column(Float)
    wind_direction_80m = Column(Float)
    wind_direction_120m = Column(Float)
    wind_gusts_10m = Column(Float)
    created_at = Column(TIMESTAMP(timezone=True), default=lambda: datetime.now(timezone.utc))

    kitespot = relationship("KiteSpot", back_populates="weather_data") 