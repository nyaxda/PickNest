#!/usr/bin/env python3
"""Unittest Module for Payments"""

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

import unittest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from models.basemodel import Base
from models.payments import Payments
from models.orders import Orders
from models.client import Client
from models.address import Address


class PaymentsTestCase(unittest.TestCase):
    def setUp(self):
        """Set up test database and session"""
        self.engine = create_engine('sqlite:///:memory:')  # In-memory SQLite database
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        self.session = self.Session()

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

        # Create an order for testing payment
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

    def test_payment_creation(self):
        """Test creating a Payments instance"""
        payment = Payments(
            public_id='payment123',
            order_id=self.order.public_id,
            payment_date=datetime.utcnow(),  # Using datetime.utcnow()
            amount_paid=100,
            payment_method='Credit Card',
            status='Completed',
            transaction_reference_number='txn123',
            Currency='USD'
        )
        self.session.add(payment)
        self.session.commit()

        # Check that the payment was successfully created
        retrieved_payment = self.session.query(Payments).filter_by(public_id='payment123').first()
        self.assertIsNotNone(retrieved_payment)
        self.assertEqual(retrieved_payment.amount_paid, 100)
        self.assertEqual(retrieved_payment.payment_method, 'Credit Card')

    def test_payment_update_status(self):
        """Test updating a payment's status"""
        payment = Payments(
            public_id='payment123',
            order_id=self.order.public_id,
            payment_date=datetime.utcnow(),  # Using datetime.utcnow()
            amount_paid=100,
            payment_method='Credit Card',
            status='Completed',
            transaction_reference_number='txn123',
            Currency='USD'
        )
        self.session.add(payment)
        self.session.commit()

        # Update the payment status
        payment.status = 'Flagged'
        self.session.commit()

        # Check that the status was updated
        updated_payment = self.session.query(Payments).filter_by(public_id='payment123').first()
        self.assertEqual(updated_payment.status, 'Flagged')

    def test_payment_relationship(self):
        """Test the relationship between Payments and Orders"""
        payment = Payments(
            public_id='payment123',
            order_id=self.order.public_id,
            payment_date=datetime.utcnow(),  # Using datetime.utcnow()
            amount_paid=100,
            payment_method='Credit Card',
            status='Completed',
            transaction_reference_number='txn123',
            Currency='USD'
        )
        self.session.add(payment)
        self.session.commit()

        # Check that the payment is related to the correct order
        self.assertEqual(payment.order.public_id, self.order.public_id)


if __name__ == '__main__':
    unittest.main()
