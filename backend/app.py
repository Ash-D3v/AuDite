"""
Ayurvedic Diet Management Software - Main FastAPI Application
Hackathon Winning Solution - 2024
"""

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import structlog
from contextlib import asynccontextmanager

from src.middleware.firebase_auth import FirebaseAuthMiddleware
from src.middleware.rate_limiter import RateLimiterMiddleware
from src.middleware.logger import setup_logging
from src.routers import auth, patients, diet, analytics, reports
from src.utils.exceptions import CustomException, custom_exception_handler
from src.services.firebase_client import FirebaseClient
from src.config import settings

# Setup structured logging
setup_logging()
logger = structlog.get_logger()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("Starting Ayurvedic Diet Management API")
    
    # Initialize Firebase
    try:
        firebase_client = FirebaseClient()
        await firebase_client.initialize()
        logger.info("Firebase initialized successfully")
    except Exception as e:
        logger.error("Failed to initialize Firebase", error=str(e))
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down Ayurvedic Diet Management API")

# Create FastAPI application
app = FastAPI(
    title="Ayurvedic Diet Management API",
    description="AI-powered Ayurvedic diet chart generation and patient management system",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add trusted host middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=settings.ALLOWED_HOSTS
)

# Add custom middleware
app.add_middleware(FirebaseAuthMiddleware)
app.add_middleware(RateLimiterMiddleware)

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(patients.router, prefix="/patients", tags=["Patient Management"])
app.include_router(diet.router, prefix="/diet", tags=["Diet Management"])
app.include_router(analytics.router, prefix="/analytics", tags=["Analytics"])
app.include_router(reports.router, prefix="/reports", tags=["Reports"])

# Add custom exception handler
app.add_exception_handler(CustomException, custom_exception_handler)

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Ayurvedic Diet Management API",
        "version": "1.0.0",
        "status": "active"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Check Firebase connection
        firebase_client = FirebaseClient()
        firebase_status = await firebase_client.health_check()
        
        return {
            "status": "healthy",
            "timestamp": "2024-01-01T00:00:00Z",
            "version": "1.0.0",
            "services": {
                "firebase": firebase_status,
                "ml_models": "available"  # Will be implemented
            }
        }
    except Exception as e:
        logger.error("Health check failed", error=str(e))
        raise HTTPException(status_code=503, detail="Service unavailable")

if __name__ == "__main__":
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
