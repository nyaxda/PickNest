#!/usr/bin/python3
"""Client Module"""

from sqlalchemy import Column, String
from .basemodel import BaseModel


class Client(BaseModel):
    """Client Model"""
    __tablename__ = 'client'
    firstname = Column(String(255), nullable=False)
    username = Column(String(255), nullable=False)
    hashedpassword = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False)
    phone = Column(String(30), nullable=False)
