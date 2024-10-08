#!/usr/bin/python3
"""Client Module"""

from sqlalchemy import Column, String
from sqlalchemy.orm import relationship
from .basemodel import BaseModel


class Client(BaseModel):
    """Client Model"""
    __tablename__ = 'client'
    public_id = Column(String(255), nullable=False)
    firstname = Column(String(255), nullable=False)
    username = Column(String(255), nullable=False)
    hashedpassword = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False)
    phone = Column(String(30), nullable=False)

    # Relationship to Address and Orders
    addresses = relationship("Address", back_populates="client")
    orders = relationship("Orders", back_populates="client")
