from sqlmodel import SQLModel, Field, Relationship, Column, Enum as SQLEnum
from pydantic import conint
from sqlalchemy import DateTime, func
from typing import Optional, List, Literal
from datetime import datetime
from zoneinfo import ZoneInfo
from enum import Enum

MOSCOW_TZ = ZoneInfo("Europe/Moscow")

PhoneType = conint(gt=9000000000, lt=9999999999)
    
class UserBase(SQLModel):
    id: int
    phone_id: Optional[int]
    is_admin: bool = False
    is_active: bool = False

        
class User(UserBase, table=True):
    """User table for storing user information"""

    id: int = Field(primary_key=True)  # Telegram ID
    phone_id: Optional[int] = Field(default=None,
                                    unique=True,
                                    foreign_key='phonewhitelist.phone')
    is_admin: bool = False
    is_active: bool = False
    
    phone: 'PhoneWhiteList' = Relationship(back_populates='user')
    
    time_registered: datetime = Field(default_factory=lambda: datetime.now(MOSCOW_TZ))
    time_updated: datetime = Field(sa_column=Column(DateTime(timezone=False), 
                                                    onupdate=lambda: datetime.now(MOSCOW_TZ)))

    
     
class UserRead(UserBase):
    ...

class PhoneWhiteListBase(SQLModel):
    phone: PhoneType

class PhoneWhiteList(PhoneWhiteListBase, table=True):
    phone: PhoneType = Field(primary_key=True)
    
    user: User = Relationship(back_populates='phone')


class PhoneWhiteListRead(PhoneWhiteListBase):
    user: Optional[UserRead]
    
class Chanel(SQLModel, table=True):
    id: int = Field(primary_key=True)
    target: bool = Field(default=False)
    