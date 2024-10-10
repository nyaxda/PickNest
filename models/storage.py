#!/usr/bin/python3
from sqlalchemy import create_engine
from .basemodel import BaseModel, Base, DATABASE_URI
from sqlalchemy.orm import sessionmaker, scoped_session
from .address import Address
from .client import Client
from .company import Company
from .items import Items
from .order_items import OrderItems
from .orders import Orders
from .payments import Payments


class Storage:
    """Handles Storage"""

    def __init__(self):
        """Engine creation and Scoped Session"""
        self.__engine = create_engine(DATABASE_URI)
        self.__session_factory = sessionmaker(bind=self.__engine,
                                              expire_on_commit=False)
        self.__session = scoped_session(self.__session_factory)

    def all(self, cls=None):
        """Return all objects in storage"""
        if cls:
            return self.__session.query(cls).all()
        else:
            classes = [Address, Client,
                       Company, Items,
                       OrderItems, Orders,
                       Payments]
            results = {}
            for c in classes:
                results[c.__name__] = self.__session.query(c).all()
            return results

    def new(self, obj):
        """Add object to storage"""
        self.__session.add(obj)

    def save(self):
        """Commit all changes to storage"""
        self.__session.commit()

    def delete(self, obj=None):
        """Delete object from storage"""
        if obj:
            self.__session.delete(obj)

    def reload(self):
        """Reload storage"""
        Base.metadata.create_all(self.__engine)

    def close(self):
        """Close storage"""
        self.__session.remove()

    def get(self, cls, id):
        """Get object by class and id"""
        return self.__session.query(cls).get(id)

    def rollback(self):
        """Rollback the session"""
        self.__session.rollback()

    def count(self, cls=None):
        """Count objects in storage"""
        if cls:
            return self.__session.query(cls).count()
        else:
            classes = [Address, Client,
                       Company, Items, OrderItems,
                       Orders, Payments]
            count = 0
            for c in classes:
                count += self.__session.query(c).count()
            return count


# Initialize the storage instance for use throughout the project
storage = Storage()
