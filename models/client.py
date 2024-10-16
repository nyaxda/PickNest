#!/usr/bin/python3
"""Client Module"""

from sqlalchemy import Column, String
from sqlalchemy.orm import relationship
from .basemodel import BaseModel


class Client(BaseModel):
    """Client Model"""
    __tablename__ = 'client'
    firstname = Column(String(255), nullable=False)
    middlename = Column(String(255), nullable=True)
    lastname = Column(String(255), nullable=False)
    username = Column(String(255), nullable=False, unique=True)
    hashedpassword = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False, unique=True)
    phone = Column(String(30), nullable=False, unique=True)
    role = Column(String(20), nullable=False)

    # Relationship to Address and Orders
    addresses = relationship("Address",
                             back_populates="client",
                             cascade="all, delete-orphan")
    orders = relationship("Orders",
                          back_populates="client",
                          cascade="all, delete-orphan")
