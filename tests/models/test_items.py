#!/usr/bin/env python3
"""Unittest Module for Items"""

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

import unittest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.basemodel import Base
from models.items import Items
from models.company import Company


class ItemsTestCase(unittest.TestCase):
    def setUp(self):
        """Set up test database and session"""
        self.engine = create_engine('sqlite:///:memory:')  # In-memory SQLite database
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        self.session = self.Session()

        # Create a company for testing purposes
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

    def tearDown(self):
        """Tear down test database"""
        self.session.close()
        Base.metadata.drop_all(self.engine)

    def test_items_creation(self):
        """Test creating an Item instance"""
        item = Items(
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
        self.session.add(item)
        self.session.commit()

        # Check that the item was successfully created
        retrieved_item = self.session.query(Items).filter_by(public_id='item123').first()
        self.assertIsNotNone(retrieved_item)
        self.assertEqual(retrieved_item.name, 'Test Item')
        self.assertEqual(retrieved_item.stockamount, 100)

    def test_items_update(self):
        """Test updating an Item instance"""
        item = Items(
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
        self.session.add(item)
        self.session.commit()

        # Update item's stockamount and price
        item.stockamount = 50
        item.price = 25.99
        self.session.commit()

        # Check that the item was updated
        updated_item = self.session.query(Items).filter_by(public_id='item123').first()
        self.assertEqual(updated_item.stockamount, 50)
        self.assertEqual(updated_item.price, 25.99)

    def test_items_negative_stockamount(self):
        """Test that negative stockamount raises a CheckConstraint error"""
        item = Items(
            public_id='item124',
            company_id=self.company.public_id,
            name='Invalid Item',
            stockamount=-10,  # Invalid stock amount
            initial_stock=100,
            reorder_level=10,
            price=19.99,
            description='A test item with negative stockamount',
            category='Test Category',
            SKU='SKU124'
        )
        
        # Adding this item should raise an IntegrityError due to the CheckConstraint
        with self.assertRaises(Exception):
            self.session.add(item)
            self.session.commit()

    def test_items_unique_sku(self):
        """Test that SKU uniqueness constraint is enforced"""
        item1 = Items(
            public_id='item123',
            company_id=self.company.public_id,
            name='Item 1',
            stockamount=100,
            initial_stock=100,
            reorder_level=10,
            price=19.99,
            description='First test item',
            category='Test Category',
            SKU='SKU123'
        )
        self.session.add(item1)
        self.session.commit()

        item2 = Items(
            public_id='item124',
            company_id=self.company.public_id,
            name='Item 2',
            stockamount=100,
            initial_stock=100,
            reorder_level=10,
            price=19.99,
            description='Second test item',
            category='Test Category',
            SKU='SKU123'  # Same SKU as item1
        )

        # Adding item2 with the same SKU should raise an IntegrityError
        with self.assertRaises(Exception):
            self.session.add(item2)
            self.session.commit()

if __name__ == '__main__':
    unittest.main()
