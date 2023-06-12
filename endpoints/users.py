from fastapi import APIRouter, HTTPException, Security, security, Depends, Response, Query
from starlette.responses import JSONResponse
from starlette.status import HTTP_201_CREATED, HTTP_404_NOT_FOUND, HTTP_200_OK
from fastapi_jwt_auth import AuthJWT
from sqlalchemy import select
from models.database import get_async_session
from auth.auth import auth_handler
from sqlalchemy.ext.asyncio import AsyncSession
from schemas.user_schemas import UserLogin, UserCreate
from models.models import User
from models.models import Role
from typing import List
from utils.game import start_or_restart_game
from utils.user import check_if_user_is_admin

users_router = APIRouter(
    prefix="/api/users",
    tags=["users"]
)


@users_router.post('/get_all_users', description='get all users')
async def get_all_users_endpoint(authorize: AuthJWT = Depends(),
                                 session: AsyncSession = Depends(get_async_session)):
    authorize.jwt_required()
    username = authorize.get_jwt_subject()
    await check_if_user_is_admin(username)

    s = select(User.c.username)
    result = await session.execute(s)
    users = result.scalars().all()
    return JSONResponse(status_code=HTTP_200_OK, content=users)
