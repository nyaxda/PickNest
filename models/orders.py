#!/usr/bin/python3
"""Items Module"""

from sqlalchemy import (
    Column, ForeignKey, Enum, String, Float
)
from sqlalchemy.orm import relationship
from .basemodel import BaseModel


class Orders(BaseModel):
    """Orders Model"""
    __tablename__ = 'orders'
    client_id = Column(String(255),
                       ForeignKey('client.public_id'),
                       nullable=False)
    shipping_address_id = Column(String(255),
                                 ForeignKey('address.public_id'),
                                 nullable=False)
    status = Column(Enum('Pending',
                         'Shipped',
                         'Delivered',
                         'Cancelled'), nullable=False)
    order_total = Column(Float, nullable=False, default=0)

    # Relationship to Client, Address, OrderItems, and Payments
    client = relationship("Client", back_populates="orders")
    shipping_address = relationship("Address", back_populates="orders")
    order_items = relationship("OrderItems",
                               back_populates="order")
    payment = relationship("Payments",
                           back_populates="order",
                           cascade="all, delete-orphan")
