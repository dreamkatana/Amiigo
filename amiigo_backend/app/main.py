from fastapi import FastAPI
from app.api.v1.api import api_router_v1 # Uncommented
from app.core.config import settings # Uncommented

# Initialize FastAPI app
app = FastAPI(
    title=settings.APP_NAME, # Using APP_NAME from settings
    description="API for the Amiigo Dating Application.",
    version="0.1.0", # Consider moving version to settings too
    openapi_url=f"{settings.API_V1_STR}/openapi.json" # Uncommented
)

# Placeholder for startup events (e.g., init DB, load ML models)
@app.on_event("startup")
async def startup_event():
    """
    Actions to perform on application startup.
    """
    print("Application startup: Initializing resources...")
    # Example: await init_database()
    print("Application startup complete.")

# Placeholder for shutdown events (e.g., close DB connections)
@app.on_event("shutdown")
async def shutdown_event():
    """
    Actions to perform on application shutdown.
    """
    print("Application shutdown: Cleaning up resources...")
    # Example: await close_database_connections()
    print("Application shutdown complete.")

# Include API routers
# app.include_router(api_router_v1, prefix=settings.API_V1_STR) # Will be uncommented later
app.include_router(api_router_v1, prefix=settings.API_V1_STR) # Uncommented

# Root endpoint
@app.get("/")
async def root():
    """
    Root GET endpoint. Provides a welcome message.
    """
    return {"message": "Welcome to the Amiigo API!"}

# Placeholder for health check endpoint
@app.get("/health")
async def health_check():
    """
    Health check endpoint for monitoring services.
    """
    return {"status": "healthy"}

# If you want to add other routers directly for testing before full structure:
# from .api.v1.endpoints import users_router # Example if users_router is defined
# app.include_router(users_router, prefix="/api/v1/users", tags=["users"])

# Note: Many parts are commented out and will be enabled as we build the respective components
# like config, API routers, etc.
