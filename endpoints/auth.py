from fastapi import APIRouter, HTTPException, Security, security, Depends, Response
from starlette.responses import JSONResponse
from starlette.status import HTTP_201_CREATED, HTTP_404_NOT_FOUND, HTTP_200_OK
from fastapi_jwt_auth import AuthJWT
from sqlalchemy import select
from models.database import get_async_session
from auth.auth import auth_handler
from sqlalchemy.ext.asyncio import AsyncSession
from schemas.user_schemas import UserLogin, UserCreate
from models.models import User


auth_router = APIRouter(
    prefix="/api/auth",
    tags=["auth"]
)


@auth_router.post('/registration', status_code=201,
                  description='Register new user')
async def register(user: UserCreate, session: AsyncSession = Depends(get_async_session)):
    # check if user exists
    s = select(User.c.id).where(User.c.username == user.username)
    result = await session.execute(s)
    if result.scalar() is not None:
        raise HTTPException(status_code=400, detail='Username is taken')

    hashed_password = auth_handler.get_password_hash(user.password)
    created_user = user.dict()
    created_user.pop('password')
    created_user['hashed_password'] = hashed_password

    await session.execute(User.insert().values(created_user))
    await session.commit()
    return JSONResponse(status_code=HTTP_201_CREATED, content={'message': f'User {user.username} created successfully'})


@auth_router.post('/login')
async def login(response: Response, user: UserLogin, authorize: AuthJWT = Depends(),
                session: AsyncSession = Depends(get_async_session)):
    user_found_password = (await session.execute(select(User.c.hashed_password).
                                                 where(User.c.username == user.username))).scalar()
    if user_found_password is None:
        raise HTTPException(status_code=401, detail='Invalid username and/or password')

    verified = auth_handler.verify_password(user.password, user_found_password)
    if not verified:
        raise HTTPException(status_code=401, detail='Invalid username and/or password')

    refresh_token = authorize.create_refresh_token(subject=user.username)
    access_token = authorize.create_access_token(subject=user.username)

    response = JSONResponse(status_code=HTTP_200_OK, content={'message': f'Authorization is successful'})
    authorize.set_access_cookies(access_token, response=response)
    authorize.set_refresh_cookies(refresh_token, response=response, max_age=2592000)
    return response


@auth_router.post('/refresh',
                  description='Refresh access token')
async def refresh(response: Response, authorize: AuthJWT = Depends()):
    authorize.jwt_refresh_token_required()
    current_user = authorize.get_jwt_subject()
    new_access_token = authorize.create_access_token(subject=current_user)

    response = JSONResponse(status_code=HTTP_200_OK, content={'message': f'Refresh is successful'})
    authorize.set_access_cookies(new_access_token, response=response)
    return response
