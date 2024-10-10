#!/usr/bin/python3
import unittest
import json
from flask import Flask
from api.views import app_views
from models import storage
from models.address import Address

class TestAddressAPI(unittest.TestCase):
    """Unit tests for Address API"""

    @classmethod
    def setUpClass(cls):
        """Setup test client and other configurations"""
        app = Flask(__name__)
        app.register_blueprint(app_views)
        cls.client = app.test_client()
        cls.client.testing = True
        # Create a mock client object in the database for testing
        cls.client_id = "test_client_id"
        cls.address_id = "test_address_id"

    def setUp(self):
        """Reset state for each test"""
        storage.reload()  # Ensure storage is clean before each test

    def test_get_all_addresses(self):
        """Test retrieving all addresses for a client"""
        response = self.client.get(f'/clients/{self.client_id}/addresses')
        self.assertEqual(response.status_code, 200)
        addresses = json.loads(response.data)
        self.assertIsInstance(addresses, list)

    def test_get_specific_address(self):
        """Test retrieving a specific address"""
        address = Address(client_id=self.client_id,
                          address_line1="123 Test Street",
                          city="Test City",
                          state="Test State",
                          postal_code="12345",
                          country="Test Country")
        address.save()
        response = self.client.get(f'/addresses/{address.id}')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['client_id'], self.client_id)

    def test_get_address_not_found(self):
        """Test retrieving a non-existent address"""
        response = self.client.get('/addresses/non_existent_id')
        self.assertEqual(response.status_code, 404)

    def test_create_address(self):
        """Test creating a new address"""
        payload = {
            'client_id': self.client_id,
            'address_line1': '123 New Street',
            'city': 'New City',
            'state': 'New State',
            'postal_code': '12345',
            'country': 'New Country'
        }
        response = self.client.post('/addresses',
                                    data=json.dumps(payload),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertIn('id', data)
        self.assertEqual(data['client_id'], self.client_id)

    def test_create_address_missing_field(self):
        """Test creating a new address with missing required field"""
        payload = {
            'client_id': self.client_id,
            'city': 'New City',
            'state': 'New State',
            'postal_code': '12345',
            'country': 'New Country'
        }
        response = self.client.post('/addresses',
                                    data=json.dumps(payload),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn("address_line1 is missing", data['message'])

    def test_update_address(self):
        """Test updating an existing address"""
        address = Address(client_id=self.client_id,
                          address_line1="123 Old Street",
                          city="Old City",
                          state="Old State",
                          postal_code="12345",
                          country="Old Country")
        address.save()

        payload = {
            'address_line1': '456 Updated Street',
            'city': 'Updated City'
        }
        response = self.client.put(f'/addresses/{address.id}',
                                   data=json.dumps(payload),
                                   content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['address_line1'], '456 Updated Street')
        self.assertEqual(data['city'], 'Updated City')

    def test_delete_address(self):
        """Test deleting an existing address"""
        address = Address(client_id=self.client_id,
                          address_line1="123 Delete Street",
                          city="Delete City",
                          state="Delete State",
                          postal_code="12345",
                          country="Delete Country")
        address.save()
        response = self.client.delete(f'/addresses/{address.id}')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.data), {})

    def test_delete_address_not_found(self):
        """Test deleting a non-existent address"""
        response = self.client.delete('/addresses/non_existent_id')
        self.assertEqual(response.status_code, 404)


if __name__ == "__main__":
    unittest.main()
