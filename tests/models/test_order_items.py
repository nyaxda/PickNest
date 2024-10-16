#!/usr/bin/env python3
"""Unittest Module for OrderItems"""

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

import unittest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.basemodel import Base
from models.order_items import OrderItems
from models.items import Items
from models.orders import Orders
from models.company import Company
from models.address import Address


class OrderItemsTestCase(unittest.TestCase):
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

        # Create an address for the client
        self.address = Address(
            public_id='address123',
            client_id='client123',  # Example client ID
            address_line1='456 Main St',
            city='Test City',
            state='Test State',
            postal_code='54321',
            country='Test Country'
        )
        self.session.add(self.address)
        self.session.commit()

        # Create an order with a valid shipping address and order total
        self.order = Orders(
            public_id='order123',
            client_id='client123',  # Example client ID
            shipping_address_id=self.address.public_id,  # Reference the created address
            status='Pending',
            order_total=100.0  # Placeholder value for order total
        )
        self.session.add(self.order)
        self.session.commit()


    def tearDown(self):
        """Tear down test database"""
        self.session.close()
        Base.metadata.drop_all(self.engine)

    def test_order_items_creation(self):
        """Test creating an OrderItems instance"""
        order_item = OrderItems(
            public_id='orderitem123',
            order_id=self.order.public_id,
            item_id=self.item.public_id,
            quantity_ordered=5,
            price_at_order_time=self.item.price
        )
        self.session.add(order_item)
        self.session.commit()

        # Check that the order item was successfully created
        retrieved_order_item = self.session.query(OrderItems).filter_by(public_id='orderitem123').first()
        self.assertIsNotNone(retrieved_order_item)
        self.assertEqual(retrieved_order_item.quantity_ordered, 5)
        self.assertEqual(retrieved_order_item.price_at_order_time, self.item.price)

    def test_order_items_update(self):
        """Test updating an OrderItems instance"""
        order_item = OrderItems(
            public_id='orderitem123',
            order_id=self.order.public_id,
            item_id=self.item.public_id,
            quantity_ordered=5,
            price_at_order_time=self.item.price
        )
        self.session.add(order_item)
        self.session.commit()

        # Update the quantity ordered and price
        order_item.quantity_ordered = 10
        order_item.price_at_order_time = 25.99
        self.session.commit()

        # Check that the order item was updated
        updated_order_item = self.session.query(OrderItems).filter_by(public_id='orderitem123').first()
        self.assertEqual(updated_order_item.quantity_ordered, 10)
        self.assertEqual(updated_order_item.price_at_order_time, 25.99)

    def test_order_items_invalid_quantity(self):
        """Test that quantity_ordered cannot be less than 1"""
        order_item = OrderItems(
            public_id='orderitem124',
            order_id=self.order.public_id,
            item_id=self.item.public_id,
            quantity_ordered=0,  # Invalid quantity
            price_at_order_time=self.item.price
        )
        
        # Adding this order item should raise an IntegrityError due to CheckConstraint
        with self.assertRaises(Exception):
            self.session.add(order_item)
            self.session.commit()

if __name__ == '__main__':
    unittest.main()
