from typing import Optional,List
from pydantic import BaseModel

class CategoryItem(BaseModel):
    name: str
    code: str

class ProductItem(BaseModel):
    id: int
    name: str
    code: str
    image: str
    thumbnail: str
    categories: list[CategoryItem]
    description: Optional[str]
    countries: List[str]
    created_at: Optional[int]

class ProductResponse(BaseModel):
    authorized: bool
    data: ProductItem


class ProductsResponse(BaseModel):
    authorized: bool
    data: list[ProductItem]
    

class ProductSellerItem(BaseModel):
    id: int
    code: str
    summary: str
    # images: List[str]
    profile_score: int
    country: str
    business_types: List[str]
    supply_count: int
    employee_count: Optional[int]
    created_at: Optional[int]

class ProductSellerResponse(BaseModel):
    authorized: bool
    data: List[ProductSellerItem]