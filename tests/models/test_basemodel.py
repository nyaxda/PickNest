#!/usr/bin/env python3
"""Unittest Module for BaseModel"""

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

import unittest
from models.basemodel import BaseModel, Base
from sqlalchemy import create_engine, Column, String
from sqlalchemy.orm import sessionmaker
from datetime import datetime


class ConcreteModel(BaseModel):
    """Concrete subclass of BaseModel for testing purposes"""
    __tablename__ = 'concrete_model'
    # You can add some extra fields for testing purposes if needed
    extra_field = Column(String(255), nullable=True)


class BaseTestCase(unittest.TestCase):
    def setUp(self):
        """Set up test database and session"""
        self.engine = create_engine('sqlite:///:memory:')  # In-memory SQLite database
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        self.session = self.Session()

    def tearDown(self):
        """Tear down test database"""
        self.session.close()
        Base.metadata.drop_all(self.engine)

    def test_basemodel_save(self):
        """Test saving an instance of ConcreteModel"""
        # Create a ConcreteModel instance
        instance = ConcreteModel()
        instance.public_id = 'test_id'
        
        # Save the instance to the session
        self.session.add(instance)
        self.session.commit()

        # Check that created_at and updated_at are set
        self.assertIsInstance(instance.created_at, datetime)
        self.assertIsInstance(instance.updated_at, datetime)
        self.assertEqual(instance.public_id, 'test_id')

    def test_basemodel_to_dict(self):
        """Test the to_dict method of ConcreteModel"""
        # Create a ConcreteModel instance
        instance = ConcreteModel(public_id='test_id')
        
        # Add and commit to the session
        self.session.add(instance)
        self.session.commit()

        # Convert to dictionary
        model_dict = instance.to_dict()

        # Check that the dictionary contains the right fields
        self.assertIn('public_id', model_dict)
        self.assertIn('created_at', model_dict)
        self.assertIn('updated_at', model_dict)
        self.assertEqual(model_dict['public_id'], 'test_id')

    def test_basemodel_update(self):
        """Test updating an instance of ConcreteModel"""
        instance = ConcreteModel(public_id='test_id')
        
        # Add to session and commit
        self.session.add(instance)
        self.session.commit()

        # Modify the instance and update
        old_updated_at = instance.updated_at
        instance.public_id = 'updated_id'
        self.session.commit()

        # Check if public_id was updated
        self.assertEqual(instance.public_id, 'updated_id')
        self.assertNotEqual(instance.updated_at, old_updated_at)


if __name__ == '__main__':
    unittest.main()
