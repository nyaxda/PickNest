#!/usr/bin/python3
"""Items moddel module"""

from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship
from .basemodel import BaseModel
from models import storage


class Items(BaseModel):
    """Items Model"""
    __tablename__ = 'items'
    public_id = Column(String(255), nullable=False, unique=True)
    company_id = Column(String(255), ForeignKey('company.public_id'), nullable=False)
    name = Column(String(255), nullable=False)
    stockamount = Column(Integer, nullable=False)
    initial_stock = Column(Integer, nullable=False)
    reorder_level = Column(Integer, nullable=False)
    description = Column(String(255), nullable=False)
    category = Column(String(255), nullable=False)
    SKU = Column(String(255), nullable=False, unique=True)

    # Relationship to Company and OrderItems
    company = relationship("Company", back_populates="items")
    order_items = relationship("OrderItems", back_populates="item")  # Note: back_populates="item"

    def update_stock(self, quantity_ordered):
        """Updates the stock when an order is placed"""
        if self.stockamount < quantity_ordered:
            raise ValueError("Insufficient stock for item")
        self.stockamount -= quantity_ordered
        storage.save()

    def restock(self, quantity_stocked):
        """Increases stock amount when an item is ordered"""
        self.stockamount += quantity_stocked
        storage.save()

    def check_reorder(self):
        """A module to check if the item is below the reorder level to
        alert the company to restock"""
        if self.stockamount < self.reorder_level:
            print(f"Item {self.name} is below the reorder level")
