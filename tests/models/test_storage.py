#!/usr/bin/env python3
"""Unittest Module for Storage"""

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

import unittest
from models.storage import storage
from models.address import Address
from models.client import Client
from sqlalchemy.orm import scoped_session


class TestStorage(unittest.TestCase):
    """Test the Storage class"""

    def setUp(self):
        """Set up for tests"""
        storage.reload()  # Ensure the database is created fresh for each test

    def tearDown(self):
        """Tear down test"""
        storage.close()  # Ensure the session is closed after each test

    def test_storage_initialization(self):
        """Test initialization of Storage"""
        self.assertIsInstance(storage._Storage__session, scoped_session)

    def test_new_and_save(self):
        """Test adding a new object and saving it"""
        client = Client(public_id="client123", firstname="John", lastname="Doe",
                        username="johndoe", hashedpassword="hashedpwd",
                        email="john@example.com", phone="1234567890", role="customer")
        storage.new(client)
        storage.save()
        stored_client = storage.get(Client, "client123")
        self.assertIsNotNone(stored_client)
        self.assertEqual(stored_client.firstname, "John")

    def test_all(self):
        """Test all method without class and with class"""
        clients = storage.all(Client)
        self.assertIsInstance(clients, list)
        
        all_objects = storage.all()
        self.assertIsInstance(all_objects, dict)
        self.assertIn("Client", all_objects)

    def test_get(self):
        """Test retrieving a single object"""
        client = Client(public_id="client124", firstname="Jane", lastname="Doe",
                        username="janedoe", hashedpassword="hashedpwd",
                        email="jane@example.com", phone="9876543210", role="customer")
        storage.new(client)
        storage.save()
        retrieved_client = storage.get(Client, "client124")
        self.assertEqual(retrieved_client.firstname, "Jane")

    def test_delete(self):
        """Test deleting an object"""
        client = Client(public_id="client125", firstname="Mark", lastname="Smith",
                        username="marksmith", hashedpassword="hashedpwd",
                        email="mark@example.com", phone="0123456789", role="customer")
        storage.new(client)
        storage.save()
        storage.delete(client)
        storage.save()
        self.assertIsNone(storage.get(Client, "client125"))

    def test_count(self):
        """Test counting objects in storage"""
        count_before = storage.count(Client)
        client = Client(public_id="client126", firstname="Lucy", lastname="Brown",
                        username="lucybrown", hashedpassword="hashedpwd",
                        email="lucy@example.com", phone="1122334455", role="customer")
        storage.new(client)
        storage.save()
        count_after = storage.count(Client)
        self.assertEqual(count_after, count_before + 1)

    def test_rollback(self):
        """Test rolling back a session"""
        client = Client(public_id="client127", firstname="Lucas", lastname="White",
                        username="lucaswhite", hashedpassword="hashedpwd",
                        email="lucas@example.com", phone="9988776655", role="customer")
        storage.new(client)
        storage.rollback()  # Rolling back should discard the new client
        storage.save()
        self.assertIsNone(storage.get(Client, "client127"))


if __name__ == "__main__":
    unittest.main()
