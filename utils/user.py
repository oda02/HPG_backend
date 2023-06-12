
from fastapi import HTTPException

from models.database import async_session_maker
from models.models import User, Gameboard, Role
from sqlalchemy import select, update


async def check_if_user_is_admin(username: str):
    """
    Checks if the user is an admin
    """
    async with async_session_maker() as session:
        stmnt = select(User.c.role).where(User.c.username == username)
        user_role = await session.execute(stmnt)
        user_role = user_role.scalar()
        if user_role is None:
            raise HTTPException(status_code=401, detail='Unauthorized')
        if user_role != Role.ADMIN:
            raise HTTPException(status_code=403, detail='Forbidden for this user')


async def check_if_user_in_game(username: str):
    """
    Checks if the user is in current game
    """
    async with async_session_maker() as session:
        stmnt = select(Gameboard.c.user_id).join(User).where(User.c.username == username)
        user_id = await session.execute(stmnt)
        user_id = user_id.scalar()
        if user_id is None:
            raise HTTPException(status_code=422, detail='User is not in a game')
        return user_id

