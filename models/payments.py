from models import Baseclass
from sqlalchemy import Column, String, Enum, Integer, ForeignKey


class Payments(Baseclass):
    """payment class implementation"""
    __tablename__ = 'payments'

    payment_id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey(orders.id) nullable=False)
    payment_date = Column(String, nullable=False)
    amount_paid = Column(Integer, nullable=False)
    payment_date = Column(DateTime, nullable=False)
    payment_method = Column(Enum('Credit Card', 'PayPal', 'M-Pesa'))
    status = Column(Enum('Completed', 'Failed', 'Flagged'))
    transaction_reference_number = Column(Integer, nullable=False)
    Currency = Column(String, nullable='False')
