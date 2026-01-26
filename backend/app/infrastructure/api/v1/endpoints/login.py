from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.application.services.user_service import UserService
from app.core.security import create_access_token
from app.schemas.token import Token
from app.infrastructure.api.v1.deps import get_user_service


router = APIRouter()


@router.post("/access-token", response_model=Token)
async def login_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    user_service: Annotated[UserService, Depends(get_user_service)]
):
    """
    OAuth2 compatible token login, get an access token for future requests.
    """
    # OAuth2 spec uses 'username' field, but we use it for email
    user = await user_service.authenticate(
        email=form_data.username, 
        password=form_data.password
    )
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token = create_access_token(subject=user.id)
    
    return Token(
        access_token=access_token,
        token_type="bearer"
    )
