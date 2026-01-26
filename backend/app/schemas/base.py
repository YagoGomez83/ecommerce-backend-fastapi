from pydantic import BaseModel, ConfigDict


class MyBaseModel(BaseModel):
    """Base model with configuration for SQLAlchemy compatibility."""
    
    model_config = ConfigDict(from_attributes=True)
