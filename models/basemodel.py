#!/usr/bin/python3
"""Basemodel Module"""

from datetime import datetime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, Integer, DateTime, create_engine
import models

DATABASE_URI = 'mysql+pymysql://portfolio:holberton@localhost/picknest'

Base = declarative_base()


class BaseModel(Base):
    """Baseclass for other classes to inherit from"""
    # __abstract__ = True ensures that the model is not mapped to the database
    __abstract__ = True
    id = Column(Integer, primary_key=True, autoincrement=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow,
                        onupdate=datetime.utcnow)

    def save(self):
        """Save the current instance to the models.storage"""
        try:
            if not self.id:
                models.storage.new(self)
            models.storage.save()
        except Exception as e:
            models.storage.rollback()
            print(f"Error occured during save: {e}")

    def delete(self):
        """Delete instance from models.storage"""
        try:
            models.storage.delete(self)
            models.storage.save()
        except Exception as e:
            models.storage.rollback()
            print(f"Error occured during delete: {e}")

    def update(self):
        """Update instance to models.storage"""
        try:
            models.storage.save()
        except Exception as e:
            models.storage.rollback()
            print(f"Error occured during update: {e}")

    def to_dict(self):
        """Dictionary representation of instance"""
        try:
            return {column.name: getattr(
                self, column.name) for column in self.__table__.columns}
        except AttributeError as e:
            print(f"Error during conversion to dict: {e}")
            return {}
