from typing import Optional
from pydantic import BaseModel
from fastapi_jwt_auth import AuthJWT
from fastapi import Request,Depends,HTTPException


class AuthChecker(BaseModel):
    authorized: bool


class PageLimiter(BaseModel):
    page: int
    limit: int
    authorized: bool

def check_auth(request: Request,Authorize: AuthJWT = Depends()):
    headers = request.headers

    if not headers.get('authorization'):
        return False
    
    else:
        Authorize.jwt_required()
        return True

async def page_limiter(request: Request,page:Optional[int] = 0, Authorize: AuthJWT = Depends()) -> PageLimiter:
    headers = request.headers
    page    = page
    limit   = 6
    authorized = False
    
    
    if not headers.get('authorization'):
        if page >= 2:
            raise HTTPException(403,"Authorization required")

    else:
        Authorize.jwt_required()
        authorized = True
        

    return PageLimiter(page=page,limit=limit,authorized=authorized)
