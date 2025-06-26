# This file makes the 'v1' directory a Python package.
# It's a good place to aggregate all v1 routers.

from fastapi import APIRouter

# Import endpoint modules for v1 API
# from .endpoints import users, login, items # etc. (Will be uncommented as created)

# Create the main router for API v1
# api_router_v1 = APIRouter()

# Include routers from endpoint modules
# api_router_v1.include_router(login.router, tags=["login"])
# api_router_v1.include_router(users.router, prefix="/users", tags=["users"])
# api_router_v1.include_router(items.router, prefix="/items", tags=["items"])

# This file will be simplified to just importing the main v1 api router from api.py
# The actual aggregation of endpoint routers will happen in app/api/v1/api.py

# print("API v1 package initialized.")
# ``` # Removed offending backticks
