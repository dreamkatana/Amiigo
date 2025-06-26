from datetime import timedelta
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm # For form data login
from sqlalchemy.orm import Session

from app import crud, models, schemas # schemas.Token
from app.api import deps # deps.get_db
from app.core import security # security.create_access_token
from app.core.config import settings # settings.ACCESS_TOKEN_EXPIRE_MINUTES

router = APIRouter()

@router.post("/login/access-token", response_model=schemas.Token)
def login_for_access_token(
    db: Session = Depends(deps.get_db),
    form_data: OAuth2PasswordRequestForm = Depends() # Gets username & password from form data
) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests.

    Takes 'username' (which is email for this app) and 'password' as form data.
    """
    user = crud.user.authenticate(
        db, email=form_data.username, password=form_data.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    elif not crud.user.is_active(user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        subject=user.user_id, expires_delta=access_token_expires # Use user.user_id as subject
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
    }

@router.post("/login/test-token", response_model=schemas.User)
def test_token(current_user: models.User = Depends(deps.get_current_active_user)) -> Any:
    """
    Test access token.
    Requires a valid Bearer token in the Authorization header.
    Returns the current active user if the token is valid.
    """
    return current_user

# Optional: A route to "refresh" a token if you implement refresh tokens later.
# This is a more advanced topic.

# Optional: Logout route (often handled client-side by discarding the token,
# but can be implemented server-side if using token blocklists).
# @router.post("/logout")
# def logout(current_user: models.User = Depends(deps.get_current_active_user)):
#     # Add token to a blocklist or perform other server-side logout actions if any
#     return {"message": "Successfully logged out"}

```
