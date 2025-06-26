# This file makes the 'models' directory a Python package.

# Import the Base class, so it's easily accessible for model definitions
from app.db.base_class import Base

# Import all your models here to ensure they are registered with SQLAlchemy's metadata.
# This is important for Alembic migrations and for Base.metadata.create_all(engine) if used.

# Example:
from .user import User
# from .profile import Profile # Uncomment when Profile model is created
# from .interest import Interest # Uncomment when Interest model is created
# from .user_interest import UserInterest # Uncomment when UserInterest model is created
# from .swipe import Swipe # Uncomment when Swipe model is created
# from .match import Match # Uncomment when Match model is created
# from .message import Message # Uncomment when Message model is created


# You can also define __all__ if you want to control what `from app.models import *` imports
# __all__ = [
#     "Base",
#     "User",
#     # "Profile",
#     # ... other model names
# ]

print("SQLAlchemy Base and User model (partially) imported in app.models.__init__")
# ``` # Removed offending backticks
