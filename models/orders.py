#!/usr/bin/python3
"""Items Module"""

from sqlalchemy import Column, String, Integer, ForeignKey
from basemodel import BaseModel
import from enum import Enum


class OrderStatus(Enum):
    """Order Status Enum"""
    PENDING = "Pending"
    SHIPPED = "Shipped"
    DELIVERED = "Delivered"
    CANCELLED = "Cancelled"


class Orders(BaseModel):
    """Orders Model"""
    __tablename__ = 'orders'
    client_id = Column(Integer, ForeignKey('client.id'), nullable=False)
    shipping_address_id = Column(Integer,
                                 ForeignKey('address.id'), nullable=False)
    status = Column(Enum(OrderStatus), nullable=False)
