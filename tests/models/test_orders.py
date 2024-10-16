#!/usr/bin/env python3
"""Unittest Module for Orders"""

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

import unittest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.basemodel import Base
from models.orders import Orders
from models.client import Client
from models.address import Address
from models.order_items import OrderItems
from models.items import Items
from models.company import Company


class OrdersTestCase(unittest.TestCase):
    def setUp(self):
        """Set up test database and session"""
        self.engine = create_engine('sqlite:///:memory:')  # In-memory SQLite database
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        self.session = self.Session()

        # Create a company and item for testing purposes
        self.company = Company(
            public_id='company123',
            name='Test Company',
            username='testcompany',
            hashed_password='hashedpassword',
            email='company@example.com',
            phone_number='1234567890',
            address1='123 Corporate Ave',
            city='Test City',
            state='Test State',
            zip='54321',
            country='Test Country',
            role='company'
        )
        self.session.add(self.company)
        self.session.commit()

        self.item = Items(
            public_id='item123',
            company_id=self.company.public_id,
            name='Test Item',
            stockamount=100,
            initial_stock=100,
            reorder_level=10,
            price=19.99,
            description='A test item for unit testing',
            category='Test Category',
            SKU='SKU123'
        )
        self.session.add(self.item)
        self.session.commit()

        # Create a client for the order
        self.client = Client(
            public_id='client123',
            firstname='John',
            lastname='Doe',
            username='johndoe',
            hashedpassword='hashedpassword',
            email='john@example.com',
            phone='9876543210',
            role='customer'
        )
        self.session.add(self.client)
        self.session.commit()

        # Create an address for the client
        self.address = Address(
            public_id='address123',
            client_id=self.client.public_id,
            address_line1='456 Main St',
            city='Test City',
            state='Test State',
            postal_code='54321',
            country='Test Country'
        )
        self.session.add(self.address)
        self.session.commit()

        # Create an order with a valid shipping address
        self.order = Orders(
            public_id='order123',
            client_id=self.client.public_id,
            shipping_address_id=self.address.public_id,
            status='Pending',
            order_total=100.0
        )
        self.session.add(self.order)
        self.session.commit()

    def tearDown(self):
        """Tear down test database"""
        self.session.close()
        Base.metadata.drop_all(self.engine)

    def test_orders_creation(self):
        """Test creating an Orders instance"""
        order = Orders(
            public_id='order124',
            client_id=self.client.public_id,
            shipping_address_id=self.address.public_id,
            status='Shipped',
            order_total=200.0
        )
        self.session.add(order)
        self.session.commit()

        # Check that the order was successfully created
        retrieved_order = self.session.query(Orders).filter_by(public_id='order124').first()
        self.assertIsNotNone(retrieved_order)
        self.assertEqual(retrieved_order.status, 'Shipped')
        self.assertEqual(retrieved_order.order_total, 200.0)

    def test_orders_update_status(self):
        """Test updating an order's status"""
        # Update the order status
        self.order.status = 'Delivered'
        self.session.commit()

        # Check that the status was updated
        updated_order = self.session.query(Orders).filter_by(public_id='order123').first()
        self.assertEqual(updated_order.status, 'Delivered')

    def test_orders_relationships(self):
        """Test the relationships between orders, client, and address"""
        # Check the client relationship
        self.assertEqual(self.order.client.public_id, 'client123')

        # Check the address relationship
        self.assertEqual(self.order.shipping_address.public_id, 'address123')


if __name__ == '__main__':
    unittest.main()
