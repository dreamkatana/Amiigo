from fastapi import APIRouter

# Import endpoint-specific routers
from .endpoints import users as users_endpoints
from .endpoints import login as login_endpoints
# from .endpoints import profiles as profiles_endpoints # Example for future
# from .endpoints import matches as matches_endpoints # Example for future
# ... import other endpoint routers as they are created

# Create the main router for API v1.
# All routes defined in the endpoint modules will be included here.
api_router_v1 = APIRouter()

# Include the login router
# It typically doesn't have a prefix if tokenUrl is /api/v1/login/access-token
api_router_v1.include_router(login_endpoints.router, tags=["Authentication"])

# Include the users router with a prefix
api_router_v1.include_router(users_endpoints.router, prefix="/users", tags=["Users"])

# Include other routers as they are developed:
# api_router_v1.include_router(profiles_endpoints.router, prefix="/profiles", tags=["Profiles"])
# api_router_v1.include_router(matches_endpoints.router, prefix="/matches", tags=["Matches"])


# This `api_router_v1` will then be imported into `app/main.py`
# and included in the main FastAPI application instance.

# Example:
# In app/main.py:
# from app.api.v1.api import api_router_v1
# from app.core.config import settings
#
# app = FastAPI(...)
# app.include_router(api_router_v1, prefix=settings.API_V1_STR)
# ``` # Removed offending backticks
