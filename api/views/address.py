#!/usr/bin/python3
"""Address Module"""

from api.views import app_views
from models import storage
from models.address import Address
from flask import jsonify, abort, request, make_response
from .token_auth import token_required


@token_required
@app_views.route('/clients/<client_id>/addresses',
                 methods=['GET'], strict_slashes=False)
def get_client_addresses(current_user, client_id):
    """Retrieve all addresses for a specific client"""
    roles = ['admin', 'client']
    if current_user.role not in roles:
        jsonify({'Error': 'Invalid Access'}), 403

    # restricts other users from accessing other users' details
    if current_user.role == 'client' and current_user.id != client_id:
        jsonify({'Error': 'Invalid Access'}), 403

    all_addresses = storage.all(Address).values()
    list_addresses = [address.to_dict() for
                      address in all_addresses if
                      address.client_id == client_id]
    return jsonify(list_addresses)


@token_required
@app_views.route('/addresses/<address_id>',
                 methods=['GET'], strict_slashes=False)
def get_address(current_user, address_id):
    """Retrieve a specific address"""
    roles = ['admin', 'client']
    if current_user.role not in roles:
        jsonify({'Error': 'Invalid Access'}), 403

    address = storage.get(Address, address_id)
    if not address:
        abort(404, description="Address not found")

    # restricts other users from altering user details
    if current_user.role == 'client' and current_user.id != address.client_id:
        jsonify({'Error': 'Invalid Access'}), 403

    return jsonify(address.to_dict())


@token_required
@app_views.route('/addresses',
                 methods=['POST'], strict_slashes=False)
def add_address(current_user):
    """Create a new address"""
    roles = ['admin', 'client']
    if current_user.role not in roles:
        jsonify({'Error': 'Invalid Access'}), 403

    data = request.get_json()
    if not data:
        abort(400, description="Not a valid JSON")

    # restricts other users from altering user details
    if current_user.role == 'client' and current_user.id != data.get('client_id'):
        jsonify({'Error': 'Invalid Access'}), 403

    required_fields = ['client_id',
                       'address_line1', 'city',
                       'state', 'postal_code', 'country']
    for field in required_fields:
        if field not in data:
            abort(400, description=f"{field} is missing")
    instance = Address(**data)
    instance.save()
    return make_response(jsonify(instance.to_dict()), 201)


@token_required
@app_views.route('/addresses/<address_id>',
                 methods=['PUT'], strict_slashes=False)
def update_address(current_user, address_id):
    """Update an existing address"""
    roles = ['admin', 'client']
    if current_user.role not in roles:
        jsonify({'Error': 'Invalid Access'}), 403

    data = request.get_json()
    if not data:
        abort(400, description="Not a valid JSON")

     # restricts other users from altering user details
    if current_user.role == 'client' and current_user.id != data.get('client_id'):
        jsonify({'Error': 'Invalid Access'}), 403

    ignored_fields = ['id', 'created_at', 'updated_at']

    address = storage.get(Address, address_id)
    if not address:
        abort(404, description="Address not found")

    for key, value in data.items():
        if key not in ignored_fields:
            setattr(address, key, value)
    storage.save()
    return make_response(jsonify(address.to_dict()), 200)


@token_required
@app_views.route('/addresses/<address_id>',
                 methods=['DELETE'], strict_slashes=False)
def delete_address(current_user, address_id):
    """Delete an address"""
    roles = ['admin', 'client']
    if current_user.role not in roles:
        jsonify({'Error': 'Invalid Access'}), 403

    address = storage.get(Address, address_id)
    if not address:
        abort(404, description="Address not found")

    # restricts other users from altering user details
    if current_user.role == 'client' and current_user.id != address.client_id:
        jsonify({'Error': 'Invalid Access'}), 403

    storage.delete(address)
    storage.save()
    return make_response(jsonify({}), 200)
