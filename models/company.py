#!/usr/bin/python3
"""company module"""

from sqlalchemy import Column, String
from sqlalchemy.orm import relationship
from .basemodel import BaseModel


class Company(BaseModel):
    """Company Model"""
    __tablename__ = 'company'
    name = Column(String(255), nullable=False, unique=True)
    username = Column(String(255), nullable=False, unique=True)
    hashed_password = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False, unique=True)
    phone_number = Column(String(30), nullable=False, unique=True)
    address1 = Column(String(255), nullable=False)
    address2 = Column(String(255), nullable=True)
    city = Column(String(255), nullable=False)
    state = Column(String(255), nullable=False)
    zip = Column(String(20), nullable=False)
    country = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False)

    # Relationship to Items
    items = relationship("Items",
                         back_populates="company",
                         cascade="all, delete-orphan")
