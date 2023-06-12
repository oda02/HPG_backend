from typing import List
import random


from fastapi import HTTPException

from models.database import async_session_maker
from sqlalchemy import select
from models.models import User, Gameboard


async def start_or_restart_game(players: List[str]) -> None:
    """Start the game"""

    async with async_session_maker() as session:
        s = select(User.c.id).filter(User.c.username.in_(players))
        user_role = await session.execute(s)
        user_role = user_role.scalars().all()
        print(user_role)

        if len(user_role) != len(players):
            raise HTTPException(status_code=422, detail='Cannot find all players in the database')

        await session.execute(Gameboard.delete())

        await session.execute(Gameboard.insert().values([{'user_id':  user_id} for user_id in user_role]))
        await session.commit()


def roll_dice():
    """
    Rolls a dice
    """
    return random.randint(1, 12)