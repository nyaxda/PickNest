from .basemodel import BaseModel
from sqlalchemy import Column, Integer, String, ForeignKey


class Address(BaseModel):
    """Address Model"""
    __tablename__ = 'address'
    address_id = Column(Integer, primary_key=True)
    client_id = Column(Integer, ForeignKey('client.id'), nullable=False)
    address_line1 = Column(String(255), nullable=False)
    address_line2 = Column(String(255), nullable=True)
    city = Column(String(255), nullable=False)
    state = Column(String(255), nullable=False)
    postal_code = Column(String(255), nullable=False)
    country = Column(String(255), nullable=False)
