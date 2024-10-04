#!/usr/bin/python3
"""Items Module"""

from sqlalchemy import Column, Integer, ForeignKey, Enum
from .basemodel import BaseModel


class Orders(BaseModel):
    """Orders Model"""
    __tablename__ = 'orders'
    client_id = Column(Integer, ForeignKey('client.id'), nullable=False)
    shipping_address_id = Column(Integer,
                                 ForeignKey('address.id'), nullable=False)
    status = Column(Enum('Pending',
                         'Shipped', 'Delivered', 'Cancelled'), nullable=False)
