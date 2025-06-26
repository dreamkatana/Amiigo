# This file makes the 'crud' directory a Python package.

# Import CRUD functions for easier access from other modules.
# This allows `from app.crud import user` instead of `from app.crud.crud_user import user`.

from .crud_user import user
# from .crud_profile import profile # Uncomment when crud_profile.py is created
# ... other crud module imports as they are created

# You can also define __all__ if you want to control what `from app.crud import *` imports
# __all__ = [
#     "user",
#     # "profile",
#     # ... other crud object names
# ]

print("CRUD operations (user) partially imported in app.crud.__init__")
# ``` # Removed offending backticks
