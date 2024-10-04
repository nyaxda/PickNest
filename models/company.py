#!/usr/bin/python3
"""company module"""

from sqlalchemy import Column, String
from .basemodel import BaseModel


class Company(BaseModel):
    """Company Model"""
    __tablename__ = 'company'
    name = Column(String(250), nullable=False)
    username = Column(String(250), nullable=False)
    hashed_password = Column(String(250), nullable=False)
    email = Column(String(250), nullable=False)
    phone_number = Column(String(30), nullable=False)
    address1 = Column(String(250), nullable=False)
    address2 = Column(String(250), nullable=True)
    city = Column(String(250), nullable=False)
    state = Column(String(250), nullable=False)
    zip = Column(String(20), nullable=False)
    country = Column(String(250), nullable=False)
