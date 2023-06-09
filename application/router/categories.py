from fastapi import APIRouter,Depends,Request
from fastapi_jwt_auth import AuthJWT
from application.utils.categories import AllCategories
from application.models.categories import CategoryResponse

router = APIRouter(prefix='/categories')


@router.get('',tags=['Categories'])
async def get_categories(request: Request,Authorize: AuthJWT = Depends()) -> list[CategoryResponse]:
    print(request.headers)
    Authorize.jwt_required()
    return await AllCategories().call()
    

    


    