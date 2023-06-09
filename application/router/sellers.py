from typing import List
from fastapi import APIRouter,Depends
from application.models.dependencies import check_auth, page_limiter,PageLimiter
from application.models.supplies import SupplyResponse
from application.utils.supplies import GetSellersSupplies
from application.utils.sellers import SearchSellers,GetSeller
from application.models.sellers import SellerResponse,SellersResponse

router = APIRouter(prefix='/sellers',tags=['Sellers'])


@router.get('')
async def get_sellers(category='',product_id='',limiter: PageLimiter = Depends(page_limiter)) -> SellersResponse:
    response =  await SearchSellers(limiter.page,limiter.limit,category,product_id).call()
    return {'authorized':limiter.authorized,'data':response}
    
    

@router.get('/{code}')
async def get_seller(code: str,auth: bool = Depends(check_auth)) -> SellerResponse:
    response = await GetSeller(code).call()
    return {'authorized':auth,'data':response}
    
    
@router.get('/{code}/supplies')
async def get_seller_supplies(code: str,product_id: int = None,limiter: PageLimiter = Depends(page_limiter)) -> SupplyResponse:
    response = await GetSellersSupplies(limiter.page,limiter.limit,code,product_id).call()
    return {'authorized':limiter.authorized,'data':response}
    