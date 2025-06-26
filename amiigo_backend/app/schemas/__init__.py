# This file makes the 'schemas' directory a Python package.

# Import Pydantic schemas for easier access from other modules.
# This allows `from app.schemas import UserCreate` instead of `from app.schemas.user import UserCreate`.

from .user import User, UserCreate, UserUpdate, UserInDB, UserBase
from .token import Token, TokenData
# from .profile import Profile, ProfileCreate, ProfileUpdate # Uncomment when profile.py is created
# ... other schema imports as they are created

# You can also define __all__ if you want to control what `from app.schemas import *` imports
# __all__ = [
#     "User",
#     "UserCreate",
#     "UserUpdate",
#     "UserInDB",
#     "UserBase",
#     "Token",
#     "TokenData",
#     # "Profile",
#     # "ProfileCreate",
#     # "ProfileUpdate",
# ]

print("Pydantic schemas (User, Token) partially imported in app.schemas.__init__")
# ``` # Removed offending backticks
