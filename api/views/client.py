#!/usr/bin/python3
"""Client Module"""

from api.views import app_views
from models import storage
from models.client import Client
from flask import jsonify, abort, request, make_response


@app_views.route('/clients',
                 methods=['GET'], strict_slashes=False)
def get_clients():
    """Retrieve list of all clients"""
    all_clients = storage.all(Client).values()
    list_clients = [client.to_dict() for client in all_clients]
    return jsonify(list_clients)


@app_views.route('/clients/<client_id>',
                 methods=['GET'], strict_slashes=False)
def get_client(client_id):
    """Retrieves a client"""
    client = storage.get(Client, client_id)
    if not client:
        abort(404)
    return jsonify(client.to_dict())


@app_views.route('/clients',
                 methods=['POST'], strict_slashes=False)
def add_client():
    """Creates a client"""
    if not request.get_json():
        abort(400, description="This is not a valid JSON")
    required_fields = ['firstname', 'middlename', 'lastname',
                       'username', 'hashed_password',
                       'email', 'phone']
    data = request.get_json()
    for field in required_fields:
        if field not in data:
            abort(400, description=f"{field} not found")
    instance = Client(**data)
    instance.save()
    return make_response(jsonify(instance.to_dict()), 201)


@app_views.route('/clients/<client_id>',
                 methods=['PUT'], strict_slashes=False)
def update_client(client_id):
    """Updates a client"""
    if not request.get_json():
        abort(404, description="Not a valid JSON")
    ignored_fields = ['id', 'created_at', 'updated_at']

    client = storage.get(Client, client_id)
    if not client:
        abort(400, description="Client not found")
    data = request.get_json()
    for key, value in data.items():
        if key not in ignored_fields:
            setattr(client, key, value)
    storage.save()
    return make_response(jsonify(client.to_dict()), 200)


@app_views.route('/clients/<client_id>',
                 methods=['DELETE'], strict_slashes=False)
def delete_client(client_id):
    """Deletes a client"""
    client = storage.get(Client, client_id)
    if not client:
        abort(404, description="No client found")
    storage.delete(client)
    storage.save()

    return(make_response(jsonify({})), 200)
