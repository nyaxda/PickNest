#!/usr/bin/python3
"""Basemodel Module"""

from datetime import datetime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, Integer, String, DateTime
from models import storage
import uuid

DATABASE_URI = 'mysql+pymysql://portfolio:holberton@localhost/picknest'

Base = declarative_base()


class BaseModel(Base):
    """Baseclass for other classes to inherit from"""
    # __abstract__ = True ensures that the model is not mapped to the database
    __abstract__ = True
    public_id = Column(String(255), nullable=False,
                       unique=True, primary_key=True,
                       default=lambda: str(uuid.uuid4()))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow,
                        onupdate=datetime.utcnow)

    def save(self):
        """Save the current instance to the models.storage"""
        try:
            if not self.id:
                storage.new(self)
            storage.save()
        except Exception as e:
            storage.rollback()
            print(f"Error occured during save: {e}")

    def delete(self):
        """Delete instance from models.storage"""
        try:
            storage.delete(self)
            storage.save()
        except Exception as e:
            storage.rollback()
            print(f"Error occured during delete: {e}")

    def update(self):
        """Update instance to models.storage"""
        try:
            storage.save()
        except Exception as e:
            storage.rollback()
            print(f"Error occured during update: {e}")

    def to_dict(self):
        """Dictionary representation of instance"""
        try:
            return {column.name: getattr(
                self, column.name) for column in self.__table__.columns}
        except AttributeError as e:
            print(f"Error during conversion to dict: {e}")
            return {}
