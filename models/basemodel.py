#!/usr/bin/python3
"""Basemodel Module"""

from datetime import datetime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, Integer, DateTime, create_engine

DATABASE_URI = 'mysql+pymysql://portfolio:holberton@localhost/picknest'

engine = create_engine('mysql+pymysql://picknest:holberton@localhost/portfolio')

Session = sessionmaker(bind=engine)
session = Session()
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
        """Save the current instance to the storage"""
        try:
            if not self.id:
                session.add(self)
                session.commit()
        except Exception as e:
            session.rollback()
            print(f"Error occured during save: {e}")

    def delete(self):
        """Delete instance from storage"""
        try:
            session.delete(self)
            session.commit()
        except Exception as e:
            session.rollback()
            print(f"Error occured during delete: {e}")

    def update(self):
        """Update instance to storage"""
        try:
            session.commit()
        except Exception as e:
            print(f"Error occured during update: {e}")

    def to_dict(self):
        """Dictionary representation of instance"""
        try:
            return {column.name: getattr(
                self, column.name) for column in self.__table__.columns}
        except AttributeError as e:
            print(f"Error during conversion to dict: {e}")
            return {}
