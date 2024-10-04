#!/usr/bin/env python3
"""Run Module"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models.basemodel import BaseModel, Base, DATABASE_URI
from models.company import Company
from models.client import Client
from models.items import Items
from models.orders import Orders
from models.order_items import OrderItems
from models.payments import Payments
from models.address import Address

# Create SQLAlchemy engine
engine = create_engine(DATABASE_URI)

# Create a configurated session
Session = sessionmaker(bind=engine)

session = Session()

Base.metadata.create_all(engine)

print("Created successfully")
