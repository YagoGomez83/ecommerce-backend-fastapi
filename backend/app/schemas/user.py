from datetime import datetime
from typing import Optional
from pydantic import EmailStr, Field, field_validator
from .base import MyBaseModel
from app.infrastructure.database.models import UserRole


class UserBase(MyBaseModel):
    """Common user fields."""
    
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    full_name: Optional[str] = Field(None, max_length=100)
    is_active: bool = True


class UserCreate(UserBase):
    """Schema for creating a new user."""
    
    password: str = Field(..., min_length=8, max_length=64)


class UserUpdate(MyBaseModel):
    """Schema for updating an existing user. All fields are optional."""
    
    email: Optional[EmailStr] = None
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    full_name: Optional[str] = Field(None, max_length=100)
    is_active: Optional[bool] = None
    password: Optional[str] = Field(None, min_length=8, max_length=100)




class UserResponse(UserBase):
    """Schema for user responses. Excludes password for security."""
    
    id: int
    created_at: datetime
    # Cambiamos esto para que sea tolerante
    role: object = "customer" 
    
    # Este validador asegura que si llega un Enum, lo convierta a string
    @field_validator('role', mode='before', check_fields=False)
    def convert_role_to_str(cls, v):
        if hasattr(v, 'value'):
            return v.value
        return str(v)

# Necesitarás importar field_validator
from pydantic import EmailStr, Field, field_validator
