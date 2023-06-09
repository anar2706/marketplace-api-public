from typing import Optional
from pydantic import BaseModel


class SupplyProductType(BaseModel):
    name: str
    code: str

class Attribute(BaseModel):
    name: str
    verbose_name: str

class SupplyItem(BaseModel):
    id: int
    code: str
    name: str
    description: Optional[str]
    product: SupplyProductType
    attributes: list[Optional[Attribute]]
    seasons: list[Optional[str]]
    images: list[Optional[str]]
    updated_at: str


class SupplyResponse(BaseModel):
    authorized: str
    data: list[SupplyItem]
    