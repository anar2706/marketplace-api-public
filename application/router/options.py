from typing import List
from fastapi import APIRouter
from models import Countries,Faq
from application.models.options import CountryResponse,FaqResponse
from application.helpers.options import volume_units,company_types

router = APIRouter(prefix='/options')


@router.get('/countries',tags=['Options'])
async def get_countries() -> List[CountryResponse]:
    return  list(Countries.select(Countries.id,Countries.name).order_by(Countries.name.asc()).dicts())
    

@router.get('/faq',tags=['Options'])
async def get_faq() -> List[FaqResponse]:
    return list(Faq.select(Faq.question,Faq.answer).order_by(Faq.question_id.asc()).dicts())
    

@router.get('/company_types',tags=['Options'])
async def get_volume_units():
    return [{'key':key,'value':value} for key,value in company_types.items()]


@router.get('/volume_units',tags=['Options'])
async def get_volume_units():
    return [{'key':key,'value':value} for key,value in volume_units.items()]