from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime

# User schemas
class UserBase(BaseModel):
    username: str
    email: EmailStr

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    is_active: bool
    created_at: datetime

    class Config:
        orm_mode = True

# KiteSpot schemas
class KiteSpotBase(BaseModel):
    name: str
    country: str
    latitude: float
    longitude: float
    description: Optional[str] = None

class KiteSpotCreate(KiteSpotBase):
    pass

class KiteSpot(KiteSpotBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True

# FavoriteSpot schemas
class FavoriteSpotCreate(BaseModel):
    kitespot_id: int

class FavoriteSpot(BaseModel):
    id: int
    user_id: int
    kitespot_id: int
    created_at: datetime

    class Config:
        orm_mode = True

# KiteSession schemas
class KiteSessionBase(BaseModel):
    kitespot_id: int
    date: datetime
    duration_minutes: int
    kite_size: float
    wind_speed: float
    notes: Optional[str] = None

class KiteSessionCreate(KiteSessionBase):
    pass

class KiteSession(KiteSessionBase):
    id: int
    user_id: int
    created_at: datetime

    class Config:
        orm_mode = True