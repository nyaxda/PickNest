#!/usr/bin/python3
"""user view path
"""
from api.views import app_views
from models.client import Client
from models import storage
from flask import request, make_request, jsonify

@token_required
app_views.route('/clients', strict_slashes=False)
def total_clients():
    """get all clients in storage"""
    clients = storage.all(Client)

    json_clients = []

    for client in clients:
        json_clients.append(client.to_json())

    return jsonify({'clients': json_clients})

@token_required
app_views.route('/clients/<id>', strict_slashes=False)
def get_single_client(id):
    """gets a single client"""
    client = storage.get(Client, id)
    return jsonify({'client': client})

app_views.route('/clients', methods=['POST'], strict_slashes=False)
def add_client():
    """add user to database"""
    data = request.get_json()

    if not data or not data.get('username') or not data.get('password'):
        return jsonify({'message': 'Incorrect Username or Password'}), 401

    hashed = bcrypt.hashpw(
            base64.b64encode(hashlib.sha256(data.get('password')).digest()),
            bcrypt.gensalt()
            )

    client = Client(
            public_id=str(uuid.uuid4()),
            email=data.get('email'),
            hashed_password=hashed,
            full_names=data.get('full_names'),
            phone=data.get('phone'),
            )

    storage.new(client)
    storage.save()
    return jsonify({'message': 'User added successfully'})

@token_required
app_views.route('/clients/<id>', methods=['POST'], strict_slashes=False)
def update_client(id):
    """updates user"""
    data = request.get_json()
    if not data:
        return jsonify({'message': 'Invalid input'}), 404

    client = storage.get(Client, id)
    if not client:
        return jsonify({'Error': 'No Client Found'})
    # Get the client to update
    client = storage.get(Client, id)
    if not client:
        return jsonify({'Error': 'No Client Found'}), 404

    # Update only the fields provided in the request
    if data.get('email'):
        client.email = data.get('email')
    
    if data.get('full_names'):
        client.full_names = data.get('full_names')

    if data.get('phone'):
        client.phone = data.get('phone')

    if data.get('password'):
        # Hash the new password before updating
        hashed_password = bcrypt.hashpw(
            base64.b64encode(hashlib.sha256(data.get('password').encode()).digest()),
            bcrypt.gensalt()
        )
        client.hashed_password = hashed_password

    storage.save()

    return jsonify({'message': 'Client updated successfully'}), 200

@token_required
app_views.route('/clients/<id>', methods=['DELETE'], strict_slashes=False)
def update_client(id):
    """deletes user"""
    client = storage.get(Client, id)
    if not client:
        return jsonify({'Error': 'No Client Found'})

    storage.delete(client)
    storage.save()

    return jsonify({'message': 'Client deleted successfully'}), 200
