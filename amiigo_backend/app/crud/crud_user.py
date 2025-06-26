from typing import Any, Dict, Optional, Union

from sqlalchemy.orm import Session
from sqlalchemy.sql.expression import select

from app.crud.base import CRUDBase # Import the generic CRUDBase
from app.models.user import User # Import the User SQLAlchemy model
from app.schemas.user import UserCreate, UserUpdate # Import Pydantic schemas for User
from app.core.security import get_password_hash, verify_password # For password operations

class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    """
    CRUD operations for User model.
    Inherits from CRUDBase and can include user-specific methods.
    """

    def get_by_email(self, db: Session, *, email: str) -> Optional[User]:
        """
        Retrieve a user by their email address.

        :param db: SQLAlchemy database session.
        :param email: Email address of the user to retrieve.
        :return: The User model instance if found, else None.
        """
        statement = select(self.model).where(self.model.email == email)
        return db.execute(statement).scalar_one_or_none()

    def create(self, db: Session, *, obj_in: UserCreate) -> User:
        """
        Create a new user.
        Overrides the base create method to handle password hashing.

        :param db: SQLAlchemy database session.
        :param obj_in: Pydantic schema (UserCreate) containing user data.
        :return: The newly created User model instance.
        """
        # Convert Pydantic schema to a dictionary
        # Pydantic V2: obj_in_data = obj_in.model_dump()
        # Pydantic V1: obj_in_data = obj_in.dict()
        obj_in_data = obj_in.model_dump()


        # Hash the password before storing
        hashed_password = get_password_hash(obj_in.password)

        # Create a dictionary for the database object, replacing plain password with hashed one
        db_obj_data = obj_in_data.copy()
        db_obj_data["password_hash"] = hashed_password
        del db_obj_data["password"] # Remove plain password

        # Use the parent class's model to create the instance
        db_obj = self.model(**db_obj_data)

        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
        self,
        db: Session,
        *,
        db_obj: User,
        obj_in: Union[UserUpdate, Dict[str, Any]]
    ) -> User:
        """
        Update an existing user.
        Overrides the base update method to handle password hashing if a new password is provided.

        :param db: SQLAlchemy database session.
        :param db_obj: The existing User model instance to update.
        :param obj_in: Pydantic schema (UserUpdate) or dictionary containing data to update.
        :return: The updated User model instance.
        """
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            # Pydantic V2: update_data = obj_in.model_dump(exclude_unset=True)
            # Pydantic V1: update_data = obj_in.dict(exclude_unset=True)
            update_data = obj_in.model_dump(exclude_unset=True)

        # If a new password is provided, hash it and update password_hash
        if "password" in update_data and update_data["password"]:
            hashed_password = get_password_hash(update_data["password"])
            # Update password_hash in the data to be set on the model
            update_data["password_hash"] = hashed_password
            del update_data["password"] # Remove plain password from update_data

        # Call the parent class's update method with potentially modified update_data
        return super().update(db, db_obj=db_obj, obj_in=update_data)

    def authenticate(
        self, db: Session, *, email: str, password: str
    ) -> Optional[User]:
        """
        Authenticate a user by email and password.

        :param db: SQLAlchemy database session.
        :param email: User's email.
        :param password: User's plain text password.
        :return: The User model instance if authentication is successful, else None.
        """
        user = self.get_by_email(db, email=email)
        if not user:
            return None
        if not user.is_active: # Optionally check if user account is active
            return None # Or raise an exception for inactive user
        if not verify_password(password, user.password_hash):
            return None
        return user

    def is_active(self, user: User) -> bool:
        """
        Check if a user is active.
        (This is a simple helper, could also be a property on the User model itself)
        """
        return user.is_active

    def is_verified(self, user: User) -> bool:
        """
        Check if a user's email is verified.
        """
        return user.is_verified

# Instantiate the CRUDUser class for the User model
user = CRUDUser(User)

# Example usage (for testing or in services/API layers):
# db_session = SessionLocal() # Assuming SessionLocal is your session factory
#
# # Create a user
# new_user_data = UserCreate(email="test@example.com", password="password123")
# created_user = user.create(db_session, obj_in=new_user_data)
# print(f"Created user: {created_user}")
#
# # Get a user by email
# fetched_user = user.get_by_email(db_session, email="test@example.com")
# print(f"Fetched user: {fetched_user}")
#
# # Authenticate user
# authenticated_user = user.authenticate(db_session, email="test@example.com", password="password123")
# print(f"Authenticated user: {authenticated_user}")
#
# # Update user (e.g., change password)
# if authenticated_user:
#     user_update_data = UserUpdate(password="newpassword123")
#     updated_user = user.update(db_session, db_obj=authenticated_user, obj_in=user_update_data)
#     print(f"Updated user (new pass hash): {updated_user.password_hash}")
#     # Re-authenticate with new password
#     reauthenticated_user = user.authenticate(db_session, email="test@example.com", password="newpassword123")
#     print(f"Re-authenticated user: {reauthenticated_user}")

# db_session.close()
# ``` # Removed offending backticks
