from typing import Any, List

from fastapi import APIRouter, Body, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import crud, models, schemas # schemas.User, schemas.UserCreate, etc.
from app.api import deps # deps.get_db, deps.get_current_active_user
from app.core.config import settings # For specific settings if needed, e.g., email settings

router = APIRouter()


@router.post("/", response_model=schemas.User, status_code=status.HTTP_201_CREATED)
def create_user(
    *,
    db: Session = Depends(deps.get_db),
    user_in: schemas.UserCreate,
    # current_user: models.User = Depends(deps.get_current_active_superuser), # Optional: If only superusers can create users
) -> Any:
    """
    Create new user.

    - Requires email and password.
    - Email must be unique.
    """
    user = crud.user.get_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The user with this email already exists in the system.",
        )

    # Add any other pre-creation validation if necessary
    # For example, password complexity if not handled by Pydantic schema validation (though typically it is)

    created_user = crud.user.create(db, obj_in=user_in)

    # TODO: Add email verification logic here if settings.EMAILS_ENABLED is True
    # if settings.EMAILS_ENABLED and created_user.email:
    #     send_new_account_email(email_to=created_user.email, username=created_user.email, password=user_in.password)

    return created_user


@router.get("/me", response_model=schemas.User)
def read_user_me(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get current logged-in user.
    """
    # current_user is already the user model instance from the dependency
    return current_user


@router.put("/me", response_model=schemas.User)
def update_user_me(
    *,
    db: Session = Depends(deps.get_db),
    user_in: schemas.UserUpdate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update current logged-in user.
    Allows updating fields like email, password, or other profile info if on User model.
    """
    # Check if the new email (if provided) is already taken by another user
    if user_in.email and user_in.email != current_user.email:
        existing_user = crud.user.get_by_email(db, email=user_in.email)
        if existing_user and existing_user.user_id != current_user.user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="This email is already registered to another user.",
            )

    updated_user = crud.user.update(db, db_obj=current_user, obj_in=user_in)
    return updated_user


# --- Admin-only routes (example, adjust dependencies as needed) ---

# @router.get("/", response_model=List[schemas.User])
# def read_users(
#     db: Session = Depends(deps.get_db),
#     skip: int = 0,
#     limit: int = 100,
#     current_user: models.User = Depends(deps.get_current_active_superuser), # Example: Superuser only
# ) -> Any:
#     """
#     Retrieve all users. (Admin/Superuser access)
#     """
#     users = crud.user.get_multi(db, skip=skip, limit=limit)
#     return users


# @router.get("/{user_id}", response_model=schemas.User)
# def read_user_by_id(
#     user_id: int,
#     db: Session = Depends(deps.get_db),
#     current_user: models.User = Depends(deps.get_current_active_superuser), # Example: Superuser only
# ) -> Any:
#     """
#     Get a specific user by ID. (Admin/Superuser access)
#     """
#     user = crud.user.get(db, id=user_id)
#     if not user:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="The user with this ID does not exist in the system.",
#         )
#     return user

# @router.put("/{user_id}", response_model=schemas.User)
# def update_user_by_id(
#     *,
#     db: Session = Depends(deps.get_db),
#     user_id: int,
#     user_in: schemas.UserUpdate,
#     current_user: models.User = Depends(deps.get_current_active_superuser), # Example: Superuser only
# ) -> Any:
#     """
#     Update a user by ID. (Admin/Superuser access)
#     """
#     user = crud.user.get(db, id=user_id)
#     if not user:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="The user with this ID does not exist in the system",
#         )
#     # Check for email conflicts if email is being updated
#     if user_in.email and user_in.email != user.email:
#         existing_email_user = crud.user.get_by_email(db, email=user_in.email)
#         if existing_email_user and existing_email_user.user_id != user_id:
#             raise HTTPException(status_code=400, detail="Email already registered by another user.")

#     updated_user = crud.user.update(db, db_obj=user, obj_in=user_in)
#     return updated_user

# @router.delete("/{user_id}", response_model=schemas.User) # Or perhaps a status message
# def delete_user_by_id(
#     *,
#     db: Session = Depends(deps.get_db),
#     user_id: int,
#     current_user: models.User = Depends(deps.get_current_active_superuser), # Example: Superuser only
# ) -> Any:
#     """
#     Delete a user by ID. (Admin/Superuser access)
#     """
#     user_to_delete = crud.user.get(db, id=user_id)
#     if not user_to_delete:
#         raise HTTPException(status_code=404, detail="User not found")
#     if user_to_delete.user_id == current_user.user_id: # Prevent self-deletion via this admin route
#         raise HTTPException(status_code=403, detail="Superusers cannot delete themselves through this endpoint.")

#     deleted_user = crud.user.remove(db, id=user_id)
#     # You might return the deleted user object or a success message
#     return deleted_user # Or return {"message": "User deleted successfully"}

# Note: Admin routes are commented out. They would require a `is_superuser` check,
# which means adding an `is_superuser` field to the User model and corresponding logic
# in `deps.py` for `get_current_active_superuser`.
```
