from typing import List
from fastapi import APIRouter,Depends
from application.models.dependencies import check_auth, page_limiter,PageLimiter
from application.utils.products import SearchProducts,GetProduct
from application.models.products import ProductsResponse,ProductResponse

router = APIRouter(prefix='/products',tags=['Product'])



@router.get('')
async def get_products(query='',category='',limiter: PageLimiter = Depends(page_limiter)) -> ProductsResponse:
    response =  await SearchProducts(limiter.page,limiter.limit,query,category).call()
    return {'authorized':limiter.authorized,'data':response}
    
    
@router.get('/{item_id}')
async def get_product(item_id,auth: bool = Depends(check_auth)) -> ProductResponse:
    response = await GetProduct(item_id).call()
    return {'authorized':auth,'data':response}
    
