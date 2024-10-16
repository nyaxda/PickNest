#!/usr/bin/env python3
"""Unittest Module"""

import sys
import os
project_root = sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
sys.path.insert(0, project_root)

import unittest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.basemodel import Base
from models.address import Address
from models.client import Client


class BaseTestCase(unittest.TestCase):
    def setUp(self):
        """Set up test database and session"""
        self.engine = create_engine('sqlite:///:memory:')  # In-memory database for testing
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        self.session = self.Session()

    def tearDown(self):
        """Tear down test database"""
        self.session.close()
        Base.metadata.drop_all(self.engine)


class TestAddressModel(BaseTestCase):
    def test_create_address(self):
        """Test creating an address"""
        # Create a client first (since Address has a ForeignKey to Client)
        client = Client(
            public_id='client123',
            firstname='TestFirst',
            lastname='TestLast',
            username='testuser',
            hashedpassword='hashedpassword',
            email='test@example.com',
            phone='1234567890',
            role='client'
        )
        self.session.add(client)
        self.session.commit()

        # Now create an address for the client
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

        # Retrieve the address and verify the details
        retrieved_address = self.session.query(Address).first()
        self.assertIsNotNone(retrieved_address)
        self.assertEqual(retrieved_address.client_id, client.public_id)
        self.assertEqual(retrieved_address.address_line1, '123 Main St')
        self.assertEqual(retrieved_address.city, 'Test City')

    def test_address_client_relationship(self):
        """Test the relationship between address and client"""
        # Create a client
        client = Client(
            public_id='client456',
            firstname='TestFirst',
            lastname='TestLast',
            username='testuser2',
            hashedpassword='hashedpassword',
            email='test2@example.com',
            phone='0987654321',
            role='client'
        )
        self.session.add(client)
        self.session.commit()

        # Create an address
        address = Address(
            client_id=client.public_id,
            address_line1='456 Secondary St',
            address_line2='Suite 200',
            city='Another City',
            state='Another State',
            postal_code='67890',
            country='Another Country'
        )
        self.session.add(address)
        self.session.commit()

        # Retrieve the client and check the addresses relationship
        retrieved_client = self.session.query(Client).first()
        self.assertEqual(len(retrieved_client.addresses), 1)
        self.assertEqual(retrieved_client.addresses[0].address_line1, '456 Secondary St')


if __name__ == '__main__':
    unittest.main()
