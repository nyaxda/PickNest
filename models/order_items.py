#!/usr/bin/python3
"""Order Items model Module"""

from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey, Column, Integer
from .basemodel import BaseModel


class OrderItems(BaseModel):
    """handles collective order handling
    """
    __tablename__ = 'order_items'

    order_id = Column(Integer, ForeignKey('orders.id'), nullable=False)
    item_id = Column(Integer, ForeignKey('items.id'), nullable=False)
    quantity_ordered = Column(Integer, nullable=False)
    price_at_order_time = Column(Integer, nullable=False)

    # Relationship to Orders and Items
    order = relationship("Orders", back_populates="order_items")
    item = relationship("Items", back_populates="order_items")
