#!/usr/bin/python3
"""Items Module"""

from sqlalchemy import Column, Integer, ForeignKey, Enum
from sqlalchemy.orm import relationship
from .basemodel import BaseModel


class Orders(BaseModel):
    """Orders Model"""
    __tablename__ = 'orders'
    client_id = Column(Integer, ForeignKey('client.id'), nullable=False)
    shipping_address_id = Column(Integer,
                                 ForeignKey('address.id'), nullable=False)
    status = Column(Enum('Pending', 'Shipped', 'Delivered', 'Cancelled'), nullable=False)

    # Relationship to Client, Address, OrderItems, and Payments
    client = relationship("Client", back_populates="orders")
    shipping_address = relationship("Address", back_populates="orders")
    order_items = relationship("OrderItems", back_populates="order")  # Note: back_populates="order"
    payment = relationship("Payments", back_populates="order")
