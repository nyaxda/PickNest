#!/usr/bin/python3
"""Items Module"""

from sqlalchemy import Column, String, Integer, ForeignKey
from .basemodel import BaseModel


class Items(BaseModel):
    """Items Model"""
    __tablename__ = 'items'
    company_id = Column(Integer, ForeignKey('company.id'), nullable=False)
    name = Column(String(255), nullable=False)
    stockamount = Column(Integer, nullable=False)
    description = Column(String(255), nullable=False)
    category = Column(String(255), nullable=False)
    SKU = Column(String(255), nullable=False)
