from datetime import datetime
from pydantic import BaseModel, Field

class CategoryCreate(BaseModel):
    nombre: str = Field(min_length=2, max_length=120)

class CategoryResponse(CategoryCreate):
    id: int
    created_at: datetime

    model_config = {"from_attributes": True}