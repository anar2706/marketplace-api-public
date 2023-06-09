from enum import Enum
from typing import Optional,Literal
from pydantic import BaseModel,EmailStr,HttpUrl

class IndustryEnum(str, Enum):
    chemicals = 'chemicals'
    agriculture = 'agriculture'
    food_beverage = 'food_beverage'

class AccountInfoRequest(BaseModel):
    first_name: str
    last_name : str
    email: EmailStr
    phone: Optional[str]


class AccountCompanyRequest(BaseModel):
    name: str
    type : str
    location: str
    website: HttpUrl
    industry: IndustryEnum
    product_categories: list[Optional[str]]
    annual_purchasing_volume : Optional[float]