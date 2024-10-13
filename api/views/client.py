#!/usr/bin/python3
"""Client Module"""

from api.views import app_views
from models import storage
from models.client import Client
from flask import jsonify, abort, request, make_response, current_app
from sqlalchemy.exc import IntegrityError
from datetime import datetime, timedelta
import uuid
import jwt
from .token_auth import token_required
from .hash_password import hash_password, verify_password

roles = ['admin', 'client']


@app_views.route('/clients/sign_up', methods=['POST'], strict_slashes=False)
def sign_up():
    """Sign-up clients to have accounts"""
    data = request.get_json()

    # Check for required fields in the request
    required_fields = ['username', 'password', 'firstname', 'lastname', 'email', 'phone']
    for field in required_fields:
        if field not in data:
            return jsonify({'message': f'{field} is required'}), 400
        if data.get('role') and data.get('role') != 'client':
            return jsonify({'message': 'Invalid role'}), 401

    # Hash the password using bcrypt
    hashed = hash_password(data.get('password'))

    # Create new client instance
    client = Client(
        public_id=str(uuid.uuid4()),
        email=data.get('email'),
        hashedpassword=hashed.encode(),
        firstname=data.get('firstname'),
        middlename=data.get('middlename', ''),  # Optional field
        lastname=data.get('lastname'),
        username=data.get('username'),
        phone=data.get('phone'),
        role='client'
    )
    try:
        # Save the new client to storage
        storage.new(client)
        storage.save()

    except IntegrityError as e:
        storage.rollback() # Rollback session in case of an error

        # Handle unique constraint violations for username, email, or phone
        if "username" in str(e.orig):
            return jsonify({'message': 'Username already exists'}), 409
        elif "email" in str(e.orig):
            return jsonify({'message': 'Email already exists'}), 409
        elif "phone" in str(e.orig):
            return jsonify({'message': 'Phone number already exists'}), 409
        else:
            return jsonify({'message': 'An error occurred during registration'}), 500

    return jsonify({'message': 'Client registered successfully'}), 201


@app_views.route('/clients/login', methods=['POST'], strict_slashes=False)
def login():
    """Login route for clients"""
    data = request.get_json()

    if not data or not data.get('username') or not data.get('password') or not data.get('role'):
        return make_response(jsonify({'message': 'Invalid input'}), 400)

    if data.get('role') != 'client':
        return make_response(jsonify({'message': 'Invalid role'}), 401)

    # Query the client by username
    all_clients = storage.all(Client)
    user = next((client for client in all_clients if client.username == data.get('username')), None)
    if not user:
        return jsonify({'message': 'Client not found!'}), 404

    # Check if the password matches
    if not verify_password(data.get('password'), user.hashedpassword):
        return jsonify({'message': 'Incorrect Password'}), 401

    # Generate token
    token = jwt.encode({
        'public_id': user.public_id,
        'role': 'client',
        'exp': datetime.utcnow() + timedelta(minutes=120)
    }, current_app.config['SECRET_KEY'], algorithm='HS256')

    return jsonify({'message': 'Client logged in successfully',
                                 'token': token if isinstance(token, str) else token.decode('utf-8')})


@app_views.route('/clients', methods=['GET'], strict_slashes=False)
@token_required
def get_clients(current_user):
    """Retrieve list of all clients"""
    if current_user.role != 'admin':
        return jsonify({'message': 'Unauthorized access'}), 403

    all_clients = storage.all(Client)
    list_clients = [client.to_dict() for client in all_clients]
    return jsonify(list_clients)


@app_views.route('/clients/<client_id>', methods=['GET'], strict_slashes=False)
@token_required
def get_client(current_user, client_id):
    """Retrieve a client by ID"""
    if current_user.role not in roles:
        return jsonify({'message': 'Unauthorized access'}), 403

    client = storage.get(Client, client_id)
    if not client:
        return jsonify({'message': 'Client not found'}), 404
    
    if current_user.role == 'client' and current_user.public_id != client.public_id:
        return jsonify({'message': 'Unauthorized access'}), 403

    return jsonify(client.to_dict())


@app_views.route('/clients', methods=['POST'], strict_slashes=False)
@token_required
def add_client(current_user):
    """Create a new client"""
    if current_user.role != 'admin':
        return jsonify({'message': 'Unauthorized action'}), 403

    if not request.get_json():
        abort(400, description="Not a valid JSON")

    required_fields = ['firstname', 'lastname', 'username', 'hashedpassword', 'email', 'phone', 'role']
    data = request.get_json()

    for field in required_fields:
        if field not in data:
            abort(400, description=f"{field} not found")

    instance = Client(**data)
    storage.new(instance)
    storage.save()

    return make_response(jsonify(instance.to_dict()), 201)


@app_views.route('/clients/<client_id>', methods=['PUT'], strict_slashes=False)
@token_required
def update_client(current_user, client_id):
    """Updates a client"""
    # Check if the current user has the right role
    if current_user.role not in roles:
        return jsonify({'message': 'Unauthorized access'}), 403

    data = request.get_json()
    if not data:
        return jsonify({'message': 'Unauthorized access'}), 400

    ignored_fields = ['id', 'created_at']

    # Fetch the client from storage
    client = storage.get(Client, client_id)
    if not client:
        return jsonify({'message': 'Client not found'}), 404

    # Restrict access to only the client's own account if they are a client
    if current_user.role == 'client' and current_user.id != client.id:
        return jsonify({'message': 'Unauthorized access'}), 403

    for key, value in data.items():
        if key not in ignored_fields:
            if key == 'password':
                # Hash the updated password
                value = hash_password(value)
                setattr(client, 'hashedpassword', value)
            else:
                setattr(client, key, value)

    # Update the updated_at timestamp
    setattr(client, 'updated_at', datetime.utcnow()) 

    # Save changes to storage
    storage.save()

    return jsonify(client.to_dict()), 200


@app_views.route('/clients/<client_id>', methods=['DELETE'], strict_slashes=False)
@token_required
def delete_client(current_user, client_id):
    """Delete a client by ID"""
    if current_user.role not in roles:
        return jsonify({'message': 'Unauthorized action'}), 401

    client = storage.get(Client, client_id)
    if not client:
        abort(404, description="Client not found")

    if current_user.role == 'client' and current_user.public_id != client.public_id:
        return jsonify({'message': 'Unauthorized action'}), 403

    client_name = client.username
    storage.delete(client)
    storage.save()

    return jsonify({'message': f'{client_name} removed'}), 200
