from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update, delete
import models
import schemas
from typing import List, Optional

# User CRUD operations
async def create_user(db: AsyncSession, user: schemas.UserCreate):
    # In a real app, you'd hash the password
    fake_hashed_password = user.password + "notreallyhashed"
    db_user = models.User(
        username=user.username,
        email=user.email,
        hashed_password=fake_hashed_password
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user

async def get_user(db: AsyncSession, user_id: int):
    result = await db.execute(select(models.User).filter(models.User.id == user_id))
    return result.scalars().first()

async def get_user_by_email(db: AsyncSession, email: str):
    result = await db.execute(select(models.User).filter(models.User.email == email))
    return result.scalars().first()

async def get_users(db: AsyncSession, skip: int = 0, limit: int = 100):
    result = await db.execute(select(models.User).offset(skip).limit(limit))
    return result.scalars().all()

# KiteSpot CRUD operations
async def create_kitespot(db: AsyncSession, kitespot: schemas.KiteSpotCreate):
    db_kitespot = models.KiteSpot(**kitespot.dict())
    db.add(db_kitespot)
    await db.commit()
    await db.refresh(db_kitespot)
    return db_kitespot

async def get_kitespot(db: AsyncSession, kitespot_id: int):
    result = await db.execute(select(models.KiteSpot).filter(models.KiteSpot.id == kitespot_id))
    return result.scalars().first()

async def get_kitespots(db: AsyncSession, skip: int = 0, limit: int = 100):
    result = await db.execute(select(models.KiteSpot).offset(skip).limit(limit))
    return result.scalars().all()

# FavoriteSpot CRUD operations
async def create_favorite_spot(db: AsyncSession, favorite: schemas.FavoriteSpotCreate, user_id: int):
    db_favorite = models.FavoriteSpot(**favorite.dict(), user_id=user_id)
    db.add(db_favorite)
    await db.commit()
    await db.refresh(db_favorite)
    return db_favorite

async def get_user_favorites(db: AsyncSession, user_id: int):
    result = await db.execute(
        select(models.FavoriteSpot).filter(models.FavoriteSpot.user_id == user_id)
    )
    return result.scalars().all()

# KiteSession CRUD operations
async def create_kite_session(db: AsyncSession, session: schemas.KiteSessionCreate, user_id: int):
    db_session = models.KiteSession(**session.dict(), user_id=user_id)
    db.add(db_session)
    await db.commit()
    await db.refresh(db_session)
    return db_session

async def get_user_sessions(db: AsyncSession, user_id: int):
    result = await db.execute(
        select(models.KiteSession).filter(models.KiteSession.user_id == user_id)
    )
    return result.scalars().all()