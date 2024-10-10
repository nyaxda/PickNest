#!/usr/bin/python3
"""Client Module"""

from api.views import app_views
from models import storage
from models.client import Client
<<<<<<< HEAD
from flask import jsonify, abort, request, make_response, current_app
=======
from flask import jsonify, abort, request, make_response
>>>>>>> origin/main
from datetime import datetime, timedelta
import uuid
import jwt
import bcrypt
import hashlib
import base64
<<<<<<< HEAD
from .token_auth import token_required
=======
roles = ['admin', 'client']
>>>>>>> origin/main


@app_views.route('/clients/sign_up', methods=['POST'], strict_slashes=False)
def sign_up():
    """Sign-up clients to have accounts"""
    data = request.get_json()
    if not data:
        return jsonify({'Error': 'Invalid JSON'}), 400

<<<<<<< HEAD
    # Check for required fields in the request
    required_fields = ['username', 'password', 'firstname', 'lastname', 'email', 'phone', 'role']
    for field in required_fields:
        if field not in data:
            return jsonify({'message': f'{field} is required'}), 400
=======
    required_fields = ['firstname', 'middlename', 'lastname',
                       'username', 'password',
                       'email', 'phone']

    for field in required_fields:
        if field not in data:
            abort(400, description=f"{field} not found")
>>>>>>> origin/main

    # Hash the password using bcrypt
    hashed = bcrypt.hashpw(
        base64.b64encode(hashlib.sha256(data.get('password').encode()).digest()),
        bcrypt.gensalt()
    )

    # Create new client instance
    client = Client(
<<<<<<< HEAD
        public_id=str(uuid.uuid4()),
        email=data.get('email'),
        hashedpassword=hashed.decode('utf-8'),
        firstname=data.get('firstname'),
        middlename=data.get('middlename', ''),  # Optional field
        lastname=data.get('lastname'),
        username=data.get('username'),
        phone=data.get('phone'),
        role=data.get('role')
    )

    # Save the new client to storage
=======
            public_id=str(uuid.uuid4()),
            firstname=data.get('firstname'),
            middlename=data.get('middlename'),
            lastname=data.get('lastname'),
            username=data.get('username'),
            email=data.get('email'),
            hashed_password=hashed,
            phone=data.get('phone'),
            role='client'
            )

>>>>>>> origin/main
    storage.new(client)
    storage.save()

    return jsonify({'message': 'Client registered successfully'}), 201


@app_views.route('/clients/login', methods=['POST'], strict_slashes=False)
def login():
<<<<<<< HEAD
    """Login route for clients"""
=======
    """Login route for both clients"""
>>>>>>> origin/main
    data = request.get_json()

    if not data or not data.get('username') or not data.get('password'):
        return make_response(jsonify({'message': 'Invalid credentials'}), 400)

    role = data.get('role')
    if role != 'client':
        return jsonify({'message': 'Invalid role'}), 401

    # Query the client by username
    all_clients = storage.all(Client)
    user = next((client for client in all_clients if client.username == data.get('username')), None)
    if not user:
        return jsonify({'message': 'Client not found!'}), 404

    # Check if the password matches
    if not bcrypt.checkpw(data['password'].encode('utf-8'), user.hashedpassword.encode('utf-8')):
        return jsonify({'message': 'Incorrect Password'}), 401

    # Generate token
    token = jwt.encode({
        'public_id': user.public_id,
<<<<<<< HEAD
        'role': 'client',
        'exp': datetime.utcnow() + timedelta(minutes=10)
    }, current_app.config['SECRET_KEY'], algorithm='HS256')

    res = make_response(jsonify({'message': 'Client logged in successfully'}))
    res.headers['access_token'] = token if isinstance(token, str) else token.decode('utf-8')
=======
        'role': user.role,  # Include role in the token for further route protection
        'exp': datetime.utcnow() + timedelta(minutes=120)
        }, app.config['SECRET_KEY'], algorithm='HS256')

    # make response header
    res = make_response(jsonify({
        'message': f'{role.capitalize()} logged in successfully',
        'token': token.decode('utf-8') if isinstance(token, bytes) else token  # Include token in response body
    }))
    res.headers['access_token'] = token.decode('utf-8') if isinstance(token, bytes) else token
>>>>>>> origin/main
    return res


@token_required
@app_views.route('/clients', methods=['GET'], strict_slashes=False)
def get_clients(current_user):
    """Retrieve list of all clients"""
    if current_user.role != 'admin':
<<<<<<< HEAD
        return jsonify({'message': 'Unauthorized action'}), 403
=======
        return jsonify({'message': 'Unauthorized access'}), 403
>>>>>>> origin/main

    all_clients = storage.all(Client).values()
    list_clients = [client.to_dict() for client in all_clients]
    return jsonify(list_clients), 200


@token_required
<<<<<<< HEAD
@app_views.route('/clients/<client_id>', methods=['GET'], strict_slashes=False)
def get_client(current_user, client_id):
    """Retrieve a client by ID"""
    if current_user.role != 'admin':
        return jsonify({'message': 'Invalid access'}), 403

    client = storage.get(Client, client_id)
    if not client:
        abort(404, description="Client not found")

    return jsonify(client.to_dict())
=======
@app_views.route('/clients/<client_id>',
                 methods=['GET'], strict_slashes=False)
def get_client(current_user, client_id):
    """Retrieves a client based on id"""
    if current_user.role not in roles:
        return jsonify({'message': 'Unauthorized access'}), 403

    client = storage.get(Client, client_id)
    if not client:
        abort(404)
>>>>>>> origin/main

    # ensures every client has access to their account only
    if current_user == 'client' and current_user.id != client.id:
        return jsonify({'message': 'Unauthorized access'}), 403

<<<<<<< HEAD
@token_required
@app_views.route('/clients', methods=['POST'], strict_slashes=False)
=======
    return jsonify(client.to_dict()), 200


@token_authorized
@app_views.route('/clients',
                 methods=['POST'], strict_slashes=False)
>>>>>>> origin/main
def add_client(current_user):
    """Create a new client"""
    if current_user.role != 'admin':
        return jsonify({'message': 'Unauthorized action'}), 403

<<<<<<< HEAD
    if not request.get_json():
        abort(400, description="Not a valid JSON")

    required_fields = ['firstname', 'lastname', 'username', 'hashedpassword', 'email', 'phone', 'role']
    data = request.get_json()
=======
    data = request.get_json()
    if not data:
        abort(400, description="This is not a valid JSON")

    required_fields = ['firstname', 'middlename', 'lastname',
                       'username', 'password',
                       'email', 'phone']
>>>>>>> origin/main

    for field in required_fields:
        if field not in data:
            abort(400, description=f"{field} not found")

<<<<<<< HEAD
    instance = Client(**data)
    storage.new(instance)
    storage.save()

    return make_response(jsonify(instance.to_dict()), 201)


@token_required
@app_views.route('/clients/<client_id>', methods=['PUT'], strict_slashes=False)
def update_client(current_user, client_id):
    """Update an existing client"""
    if not request.get_json():
        abort(400, description="Not a valid JSON")

    ignored_fields = ['id', 'created_at', 'updated_at', 'public_id']

    client = storage.get(Client, client_id)
    if not client:
        abort(404, description="Client not found")

    data = request.get_json()
=======
    data['password'] = bcrypt.hashpw(
            base64.b64encode(hashlib.sha256(data.get('password')).digest()),
            bcrypt.gensalt()
            )

    instance = Client(**data)
    instance.save()
    return jsonify(instance.to_dict()), 201


@token_authorized
@app_views.route('/clients/<client_id>',
                 methods=['PUT'], strict_slashes=False)
def update_client(current_user, client_id):
    """Updates a client"""
    if current_user.role != roles:
        return jsonify({'message': 'Unauthorized action'}), 403

    if not request.get_json():
        abort(400, description="Not a valid JSON")
    ignored_fields = ['id', 'created_at']

    client = storage.get(Client, client_id)
    if not client:
        abort(400, description="Client not found")

    # restiction on user clients to access other client accounts
    if current_user.role == 'client' and current_user.public_id != client.public_id:
        return jsonify({'message': 'Unauthorized access'}), 403

>>>>>>> origin/main
    for key, value in data.items():
        if key not in ignored_fields:
            if key == 'password':
                # hash the updated password
                value = bcrypt.hashpw(
                        base64.b64encode(hashlib.sha256(value).digest()),
                        bcrypt.gensalt()
                        )
            setattr(client, key, value)
<<<<<<< HEAD

    storage.save()

    return make_response(jsonify(client.to_dict()), 200)
=======
    setattr(client, 'updated_at', datetime.utcnow()) # update updated_at timestamp

    storage.save()
    return jsonify(client.to_dict()), 200
>>>>>>> origin/main


@token_required
@app_views.route('/clients/<client_id>', methods=['DELETE'], strict_slashes=False)
def delete_client(current_user, client_id):
<<<<<<< HEAD
    """Delete a client by ID"""
    if current_user.role not in ['admin', 'client']:
        return jsonify({'message': 'Unauthorized action'}), 401
=======
    """Deletes a client"""
    if current_user.role not in roles:
        return jsonify({'message': 'Invalid access'}), 401
>>>>>>> origin/main

    client = storage.get(Client, client_id)
    if not client:
        abort(404, description="Client not found")

<<<<<<< HEAD
    if current_user.role == 'client' and current_user.public_id != client.public_id:
        return jsonify({'message': 'Unauthorized action'}), 403
=======
    # restiction on user clients to access other client accounts
    if current_user.role == 'client' and current_user.public_id != client.public_id:
        return jsonify({'message': 'Unauthorized action'}), 403 
>>>>>>> origin/main

    storage.delete(client)
    storage.save()

    return make_response(jsonify({}), 200)
