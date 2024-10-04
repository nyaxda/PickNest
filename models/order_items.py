from .basemodel import BaseModel
from sqlalchemy import ForeignKey, Column, Integer


class OrderItems(BaseModel):
    """handles collective order handling
    """
    __tablename__ = 'order_items'

    order_id = Column(Integer, ForeignKey('orders.id'), nullable=False)
    item_id = Column(Integer, ForeignKey('items.id'), nullable=False)
    quantity_ordered = Column(Integer, nullable=False)
    price_at_order_time = Column(Integer, nullable=False)
