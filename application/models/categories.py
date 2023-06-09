from typing import Optional
from pydantic import BaseModel


class CategoryResponse(BaseModel):
    id: int
    name: str
    code: str
    depth: int
    image: Optional[str]
    thumbnail: Optional[str]
    selectable_product_count: int
