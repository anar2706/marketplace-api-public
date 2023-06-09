from datetime import datetime
from fastapi_jwt_auth import AuthJWT
from fastapi import APIRouter,HTTPException,Depends,BackgroundTasks
from werkzeug.security import generate_password_hash, check_password_hash

from models import Users,Buyers
from application.helpers.connections import Redis_Con
from application.utils.send_email import send_email
from application.utils.auth import check_login_attempts, check_reset_password_limit, create_access_token, create_refresh_token,set_login_attempts
from application.models.auth import SignupRequest,LoginRequest,ForgetPasswordRequest,SetPasswordRequest


router = APIRouter(prefix='/auth')


@router.post('/signup',tags=['Auth'])
async def signup(arguments: SignupRequest,background_tasks: BackgroundTasks):
    user_exists = Users.select().where(Users.email==arguments.email).dicts()
    if user_exists:
        raise HTTPException(400,'User already exists.')

    user_id = Users.create(email=arguments.email,country=arguments.country,
        password=generate_password_hash(arguments.password,method='sha256'),
        type=arguments.type,created=datetime.now().timestamp()).id
    
    if arguments.type == 'buyer':
        company_id = Buyers.create(created=datetime.now().timestamp()).id

    
    Users.update(company_id=company_id).where(Users.id==user_id).execute()
    background_tasks.add_task(send_email, arguments.email,'welcome')

    return {'status':'ok'}


@router.post('/login',tags=['Auth'])
async def login(arguments: LoginRequest,Authorize: AuthJWT = Depends()):
    user = Users.select().where(Users.email==arguments.email).dicts()
    if not user:
        raise HTTPException(404,'User not found')
    
    await check_login_attempts(arguments.email)

    if not check_password_hash(user[0]['password'],arguments.password):
        await set_login_attempts(arguments.email)
        raise HTTPException(401,'Incorrect Password')
    
    user_data = user[0]
    access_token = create_access_token(Authorize,user_data)
    
    refresh_token = create_refresh_token(Authorize,user_data)

    return {'access_token':access_token,'refresh_token':refresh_token} 


@router.post('/refresh',tags=['Auth'])
async def refresh(Authorize: AuthJWT = Depends()):
    Authorize.jwt_refresh_token_required()
    jti = Authorize.get_raw_jwt()['jti']
    await Redis_Con().red.setex(jti,86400,'true')

    current_user = Authorize.get_raw_jwt()['data']
    current_user['id'] = current_user['user_id']

    access_token = create_access_token(Authorize,current_user)
    refresh_token = create_refresh_token(Authorize,current_user)

    return {'access_token':access_token,'refresh_token':refresh_token} 
    

@router.post('/reset-password',tags=['Auth'])
async def reset_password(arguments: ForgetPasswordRequest,background_tasks: BackgroundTasks):
    user = Users.select().where(Users.email==arguments.email).dicts()   
    
    if not user:
        raise HTTPException(404,'User not found')

    await check_reset_password_limit(arguments.email)
    background_tasks.add_task(send_email, arguments.email,'reset')

    return {'status':'ok'}


@router.post('/set-password',tags=['Auth'])
async def set_password(arguments: SetPasswordRequest):
    if arguments.password != arguments.confirm_password:
        raise HTTPException(400,'Passwords should match')

    # Implement password changing
    
    