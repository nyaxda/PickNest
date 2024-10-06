from .basemodel import BaseModel
from sqlalchemy import Column, String, Enum, Integer, ForeignKey, DateTime


class Payments(BaseModel):
    """payment class implementation"""
    __tablename__ = 'payments'

    payment_id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey('orders.id'), nullable=False)
    payment_date = Column(String(255), nullable=False)
    amount_paid = Column(Integer, nullable=False)
    payment_date = Column(DateTime, nullable=False)
    payment_method = Column(Enum('Credit Card', 'PayPal', 'M-Pesa'))
    status = Column(Enum('Completed', 'Failed', 'Flagged'))
    transaction_reference_number = Column(Integer, nullable=False)
    Currency = Column(String(255), nullable='False')
