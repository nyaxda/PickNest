from models import Baseclass, Column, String, ForeignKey


class OrderItems(Baseclass):
    """handles collective order handling
    """
    __tablename__ = 'order_items'

    order_id = Column(Integer, ForeignKey('orders.id'), nullable=False)
    item_id = Column(Integer, ForeignKey(item.id), nullable=False)
    quantity_ordered = Column(Integer, nullable=False)
    price_at_order_time = Column(Integer, nullable=False)
