from typing import Literal
from pydantic import BaseModel,EmailStr,Field,validator
from fastapi import HTTPException




class SignupRequest(BaseModel):
    email: EmailStr
    password:str = Field(min_length=8)
    country: str
    company_name: str = Field(min_length=1)
    type: Literal['seller', 'buyer']



class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class ForgetPasswordRequest(BaseModel):
    email: EmailStr

class SetPasswordRequest(BaseModel):
    password: str
    confirm_password: str