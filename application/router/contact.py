from datetime import datetime
from fastapi import APIRouter
from application.models.contact import ContactRequest
from application.utils.general import send_contact_message
from models import ContactUs

router = APIRouter(prefix='/contact')


@router.post('/us',tags=['Contact'])
async def contact_us(arguments: ContactRequest):
    await send_contact_message(arguments.dict())
    ContactUs.create(name=arguments.first_name,surname=arguments.last_name,email=arguments.email,
        phone=arguments.phone,message=arguments.message,company=arguments.company,
        created=datetime.now().timestamp())
    
    return {'status':'ok'}


@router.post('/seller/{seller_code}',tags=['Contact'])
async def contact_seller(seller_code:str,arguments: dict):
    print(f'code {seller_code}')
    print(arguments)
    return {'status':'ok'}