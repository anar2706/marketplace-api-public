from typing import Optional
from pydantic import BaseModel

class SupplyingProducts(BaseModel):
    id: int
    name: str
    code: str

class SellerItem(BaseModel):
    code: str
    summary: Optional[str]
    country: str
    employee_count: Optional[int]
    supply_count: int
    sales_employee_count: Optional[int]
    business_types: list[Optional[str]]
    facility_count: int
    supplying_products: list[Optional[SupplyingProducts]]
    has_export_experience: Optional[bool]
    images: list[Optional[str]]


class SellerResponse(BaseModel):
    authorized: bool
    data: SellerItem


class SellersResponse(BaseModel):
    authorized: bool
    data: list[SellerItem]
