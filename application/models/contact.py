from typing import Optional
from pydantic import BaseModel,EmailStr

class ContactRequest(BaseModel):
    first_name: str
    last_name : str
    company: str
    email: EmailStr
    phone: Optional[str]
    message: str