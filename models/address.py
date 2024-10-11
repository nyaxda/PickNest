from .basemodel import BaseModel
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship


class Address(BaseModel):
    """Address Model"""
    __tablename__ = 'address'
    client_id = Column(Integer, ForeignKey('client.id'), nullable=False)
    address_line1 = Column(String(255), nullable=False)
    address_line2 = Column(String(255), nullable=True)
    city = Column(String(255), nullable=False)
    state = Column(String(255), nullable=False)
    postal_code = Column(String(255), nullable=False)
    country = Column(String(255), nullable=False)

    # Relationship to Client
    client = relationship("Client", back_populates="addresses")

    # Relationship to Orders
    orders = relationship("Orders", back_populates="shipping_address")
