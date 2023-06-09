from fastapi_jwt_auth import AuthJWT
from fastapi import APIRouter, Depends,HTTPException
from models import Users,Buyers
from application.models.account import AccountInfoRequest,AccountCompanyRequest

router = APIRouter(prefix='/account',tags=['Account'])


@router.post('/info')
async def update_buyer_account(arguments: AccountInfoRequest,Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    user_id = Authorize.get_raw_jwt()['sub']

    data = arguments.dict()
    data.pop('email',None)

    Users.update(**data).where(Users.id==user_id).execute()
    return {'status':'ok'}


@router.post('/buyer/company')
async def update_buyer_company(arguments: AccountCompanyRequest,Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    current_user = Authorize.get_raw_jwt()['data']

    if current_user['type'] !='buyer':
        raise HTTPException(403,'Company should be Buyer type to complete this action')

    
    data = arguments.dict()
    Buyers.update(data=data).where(Buyers.id==current_user['company_id']).execute()
    return {'status':'ok'}
