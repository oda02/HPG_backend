from fastapi import APIRouter, HTTPException, Security, security, Depends, Response, Query
from starlette.responses import JSONResponse
from starlette.status import HTTP_201_CREATED, HTTP_404_NOT_FOUND, HTTP_200_OK
from fastapi_jwt_auth import AuthJWT
from sqlalchemy import select, update
from models.database import get_async_session
from auth.auth import auth_handler
from sqlalchemy.ext.asyncio import AsyncSession
from schemas.user_schemas import UserLogin, UserCreate
from models.models import User, Gameboard
from models.models import Role
from typing import List
from utils.game import start_or_restart_game, roll_dice
from utils.user import check_if_user_is_admin, check_if_user_in_game

game_router = APIRouter(
    prefix="/api/game",
    tags=["game"]
)


@game_router.post('/start_game', description='start a game')
async def start_game_endpoint(players: List[str], authorize: AuthJWT = Depends()):
    authorize.jwt_required()
    username = authorize.get_jwt_subject()
    await check_if_user_is_admin(username)

    await start_or_restart_game(players)

    return JSONResponse(status_code=HTTP_200_OK, content={'message': f'Game started'})


@game_router.post('/make_turn', description='make player\'s turn')
async def make_turn(authorize: AuthJWT = Depends(), session: AsyncSession = Depends(get_async_session)):
    authorize.jwt_required()
    username = authorize.get_jwt_subject()

    user_id = await check_if_user_in_game(username)

    dice_result = roll_dice()
    stmnt = update(Gameboard, values={Gameboard.c.field_id: Gameboard.c.field_id + dice_result}). \
        where(Gameboard.c.user_id == user_id)
    await session.execute(stmnt)
    await session.commit()

    return JSONResponse(status_code=HTTP_200_OK, content={'message': f'Turn made'})

