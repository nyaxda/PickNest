import unittest
from unittest.mock import patch, MagicMock
from models.client import Client
import base64
import hashlib
from flask import Flask, json
from api.views import app_views
import bcrypt

class TestClient(unittest.TestCase):
    def setUp(self):
        app = Flask(__name__)
        app.register_blueprint(app_views)
        app.config['SECRET_KEY'] = 'your_secret_key'  # Ensure any necessary config
        self.client = app.test_client()
        self.client.testing = True
        self.app_context = app.app_context()  # Create app context
        self.app_context.push()  # Push the context
    
    def tearDown(self):
        """Pop the app context after each test"""
        self.app_context.pop()

    # @patch('api.views.client.storage.new')  # Mock the storage.new method
    # @patch('api.views.client.storage.save')  # Mock the storage.save method
    # def test_sign_up(self, mock_storage_save, mock_storage_new):
    #     # Mock the new and save methods of the storage
    #     mock_storage_new.return_value = None
    #     mock_storage_save.return_value = None

    #     data = {
    #         "firstname": "John",
    #         "lastname": "Doe",
    #         "middlename": "Middle",  # Optional field
    #         "username": "test_user",
    #         "password": "test_password",
    #         "email": "john.doe@example.com",
    #         "phone": "1234567890",
    #         "role": "client"
    #     }
    #     response = self.client.post('/api/clients/sign_up', json=data)  # Updated route with '/api' prefix
    #     self.assertEqual(response.status_code, 201)  # Status code for created resource
    #     response_data = json.loads(response.data)
    #     self.assertIn('message', response_data)
    #     self.assertEqual(response_data['message'], 'Client registered successfully')

    #     # Check that storage.new and storage.save were called
    #     mock_storage_new.assert_called_once()
    #     mock_storage_save.assert_called_once()

    # @patch('api.views.client.storage.all')  # Mock the storage.all method
    # def test_login(self, mock_storage_all):
    #     # Simplify the hashed password to be explicitly known
    #     hashed_password = bcrypt.hashpw(
    #         "test_password".encode('utf-8'), bcrypt.gensalt()
    #     ).decode('utf-8')

    #     mock_user = MagicMock()
    #     mock_user.username = "test_user"
    #     mock_user.hashedpassword = hashed_password
    #     mock_user.public_id = "1234"
    #     mock_user.role = "client"
        
    #     # Return the mock user when storage.all(Client) is called
    #     mock_storage_all.return_value = [mock_user]

    #     # Simulate login data
    #     data = {
    #         "username": "test_user",
    #         "password": "test_password",  # This password should match the one hashed
    #         "role": "client"
    #     }
        
    #     # Send POST request to login
    #     response = self.client.post('/api/clients/login', json=data)
        
    #     # Output response details for debugging
    #     print(f"Response status: {response.status_code}")
    #     print(f"Response data: {response.data.decode('utf-8')}")
        
    #     # Check if we receive a 200 status code
    #     self.assertEqual(response.status_code, 200)
        
    #     # Check that the response contains the correct message
    #     response_data = json.loads(response.data)
    #     self.assertIn('message', response_data)
    #     self.assertEqual(response_data['message'], 'Client logged in successfully')

    #     # Assert that an access token is included in the response headers
    #     self.assertIn('access_token', response.headers)

    @patch('api.views.client.storage.get')  # Mock the storage.get method
    @patch('api.views.client.token_required')  # Bypass token_required decorator
    def test_get_client(self, mock_token_required, mock_storage_get):
        """Test get_client route"""

        # Simulate a current_user with an admin role
        mock_current_user = MagicMock()
        mock_current_user.role = 'admin'

        # Mock the token_required decorator to return mock_current_user
        mock_token_required.side_effect = lambda f: lambda *args, **kwargs: f(mock_current_user, *args, **kwargs)
    
        # Mock a client object returned from storage.get
        mock_client_instance = MagicMock()
        mock_client_instance.to_dict.return_value = {
            'id': '1', 'username': 'user1', 'role': 'client'
        }
        mock_storage_get.return_value = mock_client_instance  # Mock storage.get return value

        # Perform a GET request to the /api/clients/1 route
        print("Sending GET request to /api/clients/1")
        response = self.client.get('/api/clients/1', headers={'access_token': 'valid_token'})
        
        # Check the status code and response data
        print("Response status code:", response.status_code)
        print("Response data:", response.data)
        
        self.assertEqual(response.status_code, 200)  # Assert that status code is 200 OK
        response_data = json.loads(response.data)  # Load the response JSON data
        print("Extracted response data:", response_data)
        self.assertEqual(response_data['username'], 'user1')  # Check the client's username
        self.assertEqual(response_data['id'], '1')  # Check the client's ID

if __name__ == '__main__':
    unittest.main()
