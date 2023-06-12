import datetime
import enum
import uuid
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import MetaData, Table, Column, Integer, String, TIMESTAMP, ForeignKey, JSON, Boolean, Enum
from sqlalchemy_utils import URLType
# from models.database import metadata_obj
from sqlalchemy import MetaData

metadata_obj = MetaData()


class Role(enum.Enum):
    ADMIN = 1
    USER = 2


User = Table(
    "user",
    metadata_obj,
    Column("id", UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4),
    Column("username", String, nullable=False, index=True),
    Column("hashed_password", String, nullable=False),
    Column("description", String, default=""),
    Column("is_active", Boolean, default=True),
    Column("real_name", String, nullable=False),
    Column("real_surname", String, nullable=False),
    Column("vk_link", String, nullable=False),
    Column("score", Integer, default=0),
    Column("completed_rounds", Integer, default=0),
    Column("role", Enum(Role), default=Role.USER, nullable=False),
)


Gameboard = Table(
    "gameboard",
    metadata_obj,
    Column("user_id", UUID(as_uuid=True), ForeignKey("user.id"), primary_key=True, index=True, nullable=False,
           unique=True),
    Column("field_id", Integer, index=True, default=0, nullable=False),
    Column("enter_datetime", TIMESTAMP, nullable=False, default=datetime.datetime.utcnow),
)
