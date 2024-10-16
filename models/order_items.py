#!/usr/bin/python3
"""Order Items model Module"""

from sqlalchemy.orm import relationship
from sqlalchemy import (
    ForeignKey, Column, Integer,
    String, Float, CheckConstraint
)
from .basemodel import BaseModel


class OrderItems(BaseModel):
    """handles collective order handling
    """
    __tablename__ = 'order_items'

    order_id = Column(String(255),
                      ForeignKey('orders.public_id'),
                      nullable=False)
    item_id = Column(String(255),
                     ForeignKey('items.public_id'),
                     nullable=False)
    quantity_ordered = Column(Integer, nullable=False)
    price_at_order_time = Column(Float, nullable=False)

    # Add CheckConstraints to ensure no negative values
    __table_args__ = (
        CheckConstraint('quantity_ordered >= 1',
                        name='check_quantity_ordered_gt0'),
    )
    # Relationship to Orders and Items
    order = relationship("Orders", back_populates="order_items")
    item = relationship("Items", back_populates="order_items")
