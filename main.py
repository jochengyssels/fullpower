import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
import logging

# Import database and models
from database import get_db, engine, Base
import models

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("railway-app")

# Lifespan context manager (replaces on_event)
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Create tables
    logger.info("Application startup")
    async with engine.begin() as conn:
        try:
            # This will create tables that don't exist yet
            await conn.run_sync(Base.metadata.create_all)
            logger.info("Database tables created successfully")
        except Exception as e:
            logger.error(f"Error creating database tables: {e}")
    
    yield  # This is where the application runs
    
    # Shutdown
    logger.info("Application shutdown")

# Create FastAPI app
app = FastAPI(
    title="Full Power API",
    description="API for the Full Power kitesurfing application",
    version="0.1.0",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Root endpoint
@app.get("/")
async def root():
    logger.info("Root endpoint called")
    return {"message": "Welcome to Full Power API"}

# Health check endpoint
@app.get("/health")
async def health_check():
    logger.info("Health check called")
    return {"status": "ok", "message": "API is running"}

# Database health check endpoint
@app.get("/health/db")
async def db_health_check(db: AsyncSession = Depends(get_db)):
    logger.info("Database health check called")
    try:
        # Simple query to test database connection
        result = await db.execute(text("SELECT 1"))
        if result.scalar() == 1:
            return {"status": "ok", "message": "Database connection successful"}
        else:
            logger.error("Database health check failed: unexpected result")
            raise HTTPException(status_code=500, detail="Database health check failed")
    except Exception as e:
        logger.error(f"Database health check failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Database connection failed: {str(e)}")

# Run the application
if __name__ == "__main__":
    import uvicorn
    
    port = int(os.environ.get("PORT", 8000))
    logger.info(f"Starting server on port {port}")
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False)
