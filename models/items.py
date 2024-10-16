#!/usr/bin/python3
"""Items moddel module"""

from sqlalchemy import (
    Column, String, Integer, ForeignKey,
    CheckConstraint, Float
)
from sqlalchemy.orm import relationship
from .basemodel import BaseModel
from models import storage


class Items(BaseModel):
    """Items Model"""
    __tablename__ = 'items'
    company_id = Column(String(255),
                        ForeignKey('company.public_id'),
                        nullable=False)
    name = Column(String(255), nullable=False)
    stockamount = Column(Integer, nullable=False)
    initial_stock = Column(Integer, nullable=False)
    reorder_level = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)
    description = Column(String(255), nullable=False)
    category = Column(String(255), nullable=False)
    SKU = Column(String(255), nullable=False, unique=True)

    # Add CheckConstraints to ensure no negative values
    __table_args__ = (
        CheckConstraint('stockamount >= 0',
                        name='check_stockamount_non_negative'),
        CheckConstraint('initial_stock >= 0',
                        name='check_initial_stock_non_negative'),
        CheckConstraint('reorder_level >= 0',
                        name='check_reorder_level_non_negative'),
    )

    # Relationship to Company and OrderItems
    company = relationship("Company", back_populates="items")
    order_items = relationship("OrderItems",
                               back_populates="item")
