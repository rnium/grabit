from pydantic import BaseModel, Field, HttpUrl
from datetime import datetime
from typing import Dict, List


class ProductBase(BaseModel):
    url: HttpUrl
    title: str | None = None
    added_at: datetime
    is_complete: bool
    site: str

class Product(ProductBase):
    id: int
    
    class Config:
        from_attributes = True

class ProductCreate(ProductBase):
    pass

class ProductRequest(BaseModel):
    url: HttpUrl | None = None
    pk: int | None = None
    

class ProductData(BaseModel):
    title: str = Field(max_length=500)
    prices: Dict[str, float]
    key_features: Dict[str, str] | List[str]
    images: List[HttpUrl]
    spec_tables: Dict[str, Dict[str, str]]
    description: str | None