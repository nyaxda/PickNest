from sqlalchemy import Column, String, Enum, Integer, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from .basemodel import BaseModel


class Payments(BaseModel):
    """payment class implementation"""
    __tablename__ = 'payments'

    order_id = Column(String(255),
                      ForeignKey('orders.public_id'),
                      nullable=False)
    payment_date = Column(String(255), nullable=False)
    amount_paid = Column(Integer, nullable=False)
    payment_date = Column(DateTime, nullable=False)
    payment_method = Column(Enum('Credit Card', 'PayPal', 'M-Pesa'),
                            nullable=False, default='Credit Card')
    status = Column(Enum('Completed', 'Failed', 'Flagged'))
    transaction_reference_number = Column(String(255), nullable=False)
    Currency = Column(String(255), nullable='False')

    # Relationship to Orders
    order = relationship("Orders", back_populates="payment")
