#!/usr/bin/env python3
"""Unittest Module for Client"""

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

import unittest
from models.basemodel import Base, BaseModel
from models.client import Client
from models.address import Address
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


class ClientTestCase(unittest.TestCase):
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

    def test_client_creation(self):
        """Test creating a Client instance"""
        client = Client(
            public_id='client123',
            firstname='John',
            lastname='Doe',
            username='johndoe',
            hashedpassword='hashedpassword',
            email='john@example.com',
            phone='1234567890',
            role='client'
        )
        self.session.add(client)
        self.session.commit()

        # Check that the client was successfully created
        retrieved_client = self.session.query(Client).filter_by(public_id='client123').first()
        self.assertIsNotNone(retrieved_client)
        self.assertEqual(retrieved_client.firstname, 'John')
        self.assertEqual(retrieved_client.lastname, 'Doe')

    def test_client_update(self):
        """Test updating a Client instance"""
        client = Client(
            public_id='client123',
            firstname='John',
            lastname='Doe',
            username='johndoe',
            hashedpassword='hashedpassword',
            email='john@example.com',
            phone='1234567890',
            role='client'
        )
        self.session.add(client)
        self.session.commit()

        # Update client's information
        client.firstname = 'Jane'
        client.lastname = 'Smith'
        self.session.commit()

        # Check that the client was updated
        updated_client = self.session.query(Client).filter_by(public_id='client123').first()
        self.assertEqual(updated_client.firstname, 'Jane')
        self.assertEqual(updated_client.lastname, 'Smith')

    def test_client_address_relationship(self):
        """Test the relationship between Client and Address"""
        client = Client(
            public_id='client123',
            firstname='John',
            lastname='Doe',
            username='johndoe',
            hashedpassword='hashedpassword',
            email='john@example.com',
            phone='1234567890',
            role='client'
        )
        self.session.add(client)
        self.session.commit()

        # Create address for the client
        address = Address(
            client_id=client.public_id,
            address_line1='123 Main St',
            address_line2='Apt 4B',
            city='Test City',
            state='Test State',
            postal_code='12345',
            country='Test Country'
        )
        self.session.add(address)
        self.session.commit()

        # Check the relationship
        self.assertEqual(len(client.addresses), 1)
        self.assertEqual(client.addresses[0].address_line1, '123 Main St')

if __name__ == '__main__':
    unittest.main()
