from datetime import datetime
from fastapi_jwt_auth import AuthJWT
from fastapi import APIRouter,Depends
from application.utils.favorites import GetFavorites
from models import FavoriteSellers
from fastapi.concurrency import run_in_threadpool

router = APIRouter(prefix='/favorites',tags=['Favorites'])

@router.get('')
async def get_favorites(Authorize: AuthJWT = Depends()) :
    Authorize.jwt_required()
    jwt_data = Authorize.get_raw_jwt()['data']    
    user_id  = jwt_data['user_id']

    return await GetFavorites(0,100,user_id).call()

@router.post('/{seller_id}')
async def add_favorite(seller_id: int,Authorize: AuthJWT = Depends()) :
    Authorize.jwt_required()
    jwt_data = Authorize.get_raw_jwt()['data']
    
    user_id  = jwt_data['user_id']
    company_id = jwt_data['company_id']

    await run_in_threadpool(FavoriteSellers.create,user_id=user_id,company_id=company_id,seller_id=seller_id,
        created=int(datetime.now().timestamp()))
    
    return {'status':'ok'}


@router.delete('/{seller_id}')
def remove_favorite(seller_id: int,Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    jwt_data = Authorize.get_raw_jwt()['data']
    user_id  = jwt_data['user_id']

    FavoriteSellers.delete().where(FavoriteSellers.user_id==user_id,
            FavoriteSellers.seller_id==seller_id).execute()
    
    return {'status':'ok'}