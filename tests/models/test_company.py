#!/usr/bin/env python3
"""Unittest Module for Company"""

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

import unittest
from models.basemodel import Base, BaseModel
from models.company import Company
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


class CompanyTestCase(unittest.TestCase):
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

    def test_company_creation(self):
        """Test creating a Company instance"""
        company = Company(
            public_id='company123',
            name='Test Company',
            username='testcompany',
            hashed_password='hashedpassword',
            email='company@example.com',
            phone_number='1234567890',
            address1='123 Corporate Ave',
            address2='Suite 100',
            city='Test City',
            state='Test State',
            zip='54321',
            country='Test Country',
            role='company'
        )
        self.session.add(company)
        self.session.commit()

        # Check that the company was successfully created
        retrieved_company = self.session.query(Company).filter_by(public_id='company123').first()
        self.assertIsNotNone(retrieved_company)
        self.assertEqual(retrieved_company.name, 'Test Company')
        self.assertEqual(retrieved_company.email, 'company@example.com')

    def test_company_update(self):
        """Test updating a Company instance"""
        company = Company(
            public_id='company123',
            name='Test Company',
            username='testcompany',
            hashed_password='hashedpassword',
            email='company@example.com',
            phone_number='1234567890',
            address1='123 Corporate Ave',
            address2='Suite 100',
            city='Test City',
            state='Test State',
            zip='54321',
            country='Test Country',
            role='company'
        )
        self.session.add(company)
        self.session.commit()

        # Update company's information
        company.name = 'Updated Company'
        company.city = 'Updated City'
        self.session.commit()

        # Check that the company was updated
        updated_company = self.session.query(Company).filter_by(public_id='company123').first()
        self.assertEqual(updated_company.name, 'Updated Company')
        self.assertEqual(updated_company.city, 'Updated City')

    def test_company_email_unique(self):
        """Test that email uniqueness constraint is enforced"""
        company1 = Company(
            public_id='company123',
            name='Test Company 1',
            username='testcompany1',
            hashed_password='hashedpassword1',
            email='unique@example.com',
            phone_number='1234567890',
            address1='123 Corporate Ave',
            address2='Suite 100',
            city='Test City',
            state='Test State',
            zip='54321',
            country='Test Country',
            role='company'
        )
        company2 = Company(
            public_id='company124',
            name='Test Company 2',
            username='testcompany2',
            hashed_password='hashedpassword2',
            email='unique@example.com',  # Same email as company1
            phone_number='0987654321',
            address1='124 Corporate Ave',
            address2='Suite 200',
            city='Other City',
            state='Other State',
            zip='12345',
            country='Other Country',
            role='company'
        )
        self.session.add(company1)
        self.session.commit()

        # Adding company2 with the same email should raise an IntegrityError
        with self.assertRaises(Exception):
            self.session.add(company2)
            self.session.commit()

if __name__ == '__main__':
    unittest.main()
