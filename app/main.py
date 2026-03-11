"""Main FastAPI Application"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from config import get_settings
from app.routes import orders, payments

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI application
app = FastAPI(
    title="Payment Service API",
    description="Service for managing order payments",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Include routers
app.include_router(orders.router, prefix="/api", tags=["Orders"])
app.include_router(payments.router, prefix="/api", tags=["Payments"])


@app.on_event("startup")
async def startup_event():
    """Application startup event"""
    settings = get_settings()
    logger.info(f"Starting Payment Service API")
    logger.info(f"Database: {settings.database_url}")
    logger.info(f"Bank API: {settings.bank_api_base_url}")


@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown event"""
    logger.info("Shutting down Payment Service API")


@app.get("/", tags=["Health"])
async def root():
    """Health check endpoint"""
    return {
        "message": "Payment Service API is running",
        "status": "healthy",
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "payment-service",
    }


if __name__ == "__main__":
    import uvicorn

    settings = get_settings()
    uvicorn.run(
        "app.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.api_debug,
    )
