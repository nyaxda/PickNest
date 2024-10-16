#!/usr/bin/python3
"""Address Module"""

from api.views import app_views
from models import storage
from models.address import Address
from sqlalchemy.exc import IntegrityError
from flask import jsonify, request
from .token_auth import token_required
import uuid


@app_views.route('/clients/<client_id>/addresses',
                 methods=['GET'], strict_slashes=False)
@token_required
def get_client_addresses(current_user, client_id):
    """Retrieve all addresses for a specific client"""
    roles = ['admin', 'client']
    if current_user.role not in roles:
        return jsonify({'Error': 'Unauthorized Access'}), 403

    # restricts other users from accessing other users' details
    if current_user.role == 'client' and current_user.public_id != client_id:
        return jsonify({'Error': 'Unauthorized Access'}), 403

    all_addresses = storage.all(Address)
    list_addresses = [address.to_dict() for
                      address in all_addresses if
                      address.client_id == client_id]
    return jsonify(list_addresses)


@app_views.route('/addresses/<address_id>',
                 methods=['GET'], strict_slashes=False)
@token_required
def get_address(current_user, address_id):
    """Retrieve a specific address"""
    roles = ['admin', 'client']
    if current_user.role not in roles:
        return jsonify({'Error': 'Unauthorized Access'}), 403

    address = storage.get(Address, address_id)
    if not address:
        return jsonify({"Error": "Address not found"}), 404

    # restricts other users from altering user details
    if (current_user.role == 'client' and
            current_user.public_id != address.client_id):
        return jsonify({'Error': 'Unauthorized Access'}), 403

    return jsonify(address.to_dict())


@app_views.route('/addresses', methods=['GET'], strict_slashes=False)
@token_required
def get_all_addresses(current_user):
    """Retrieve all addresses, only accessible by admin"""
    if current_user.role != 'admin':
        return jsonify({'Error': 'Unauthorized access'}), 403

    all_addresses = storage.all(Address)
    list_addresses = [item.to_dict() for item in all_addresses]
    return jsonify(list_addresses)


@app_views.route('/addresses',
                 methods=['POST'], strict_slashes=False)
@token_required
def add_address(current_user):
    """Create a new address"""
    roles = ['admin', 'client']
    if current_user.role not in roles:
        return jsonify({'Error': 'Unauthorized Access'}), 403

    data = request.get_json()
    if not data:
        return jsonify({"Error": "Not a valid JSON"}), 400

    if (current_user.role == 'client' and
            current_user.public_id != data.get('client_id')):
        return jsonify({'Error': f'Invalid access'}), 403

    required_fields = ['client_id',
                       'address_line1', 'city',
                       'state', 'postal_code', 'country']
    for field in required_fields:
        if field not in data:
            return jsonify({"Error": f"{field} is missing"}), 400
    data["public_id"] = str(uuid.uuid4())
    instance = Address(**data)
    try:
        storage.new(instance)
        storage.save()
    except IntegrityError as e:
        return jsonify({'Error': 'Invalid data', 'message': str(e)}), 400
    return jsonify(instance.to_dict()), 201


@app_views.route('/addresses/<address_id>',
                 methods=['PUT'], strict_slashes=False)
@token_required
def update_address(current_user, address_id):
    """Update an existing address"""
    roles = ['admin', 'client']
    if current_user.role not in roles:
        return jsonify({'Error': 'Unauthorized Access'}), 403

    data = request.get_json()
    if not data:
        return jsonify({"Error": "Not a valid JSON"}), 400

    # restricts other users from altering user details
    if (current_user.role == 'client' and
            current_user.public_id != data.get('client_id')):
        return jsonify({'Error': 'Unauthorized Access'}), 403

    ignored_fields = ['id', 'created_at', 'updated_at']

    address = storage.get(Address, address_id)
    if not address:
        return jsonify({"Error": "Address not found"}), 404

    for key, value in data.items():
        if key not in ignored_fields:
            setattr(address, key, value)
    try:
        storage.save()
    except IntegrityError as e:
        return jsonify({'Error': 'Invalid data', 'message': str(e)}), 400
    return jsonify(address.to_dict()), 200


@app_views.route('/addresses/<address_id>',
                 methods=['DELETE'], strict_slashes=False)
@token_required
def delete_address(current_user, address_id):
    """Delete an address"""
    roles = ['admin', 'client']
    if current_user.role not in roles:
        return jsonify({'Error': 'Unauthorized Access'}), 403

    address = storage.get(Address, address_id)
    if not address:
        return jsonify({"Error": "Address not found"}), 404
    # restricts other users from altering user details
    if (current_user.role == 'client' and
            current_user.public_id != address.client_id):
        return jsonify({'Error': 'Unauthorized Access'}), 403

    storage.delete(address)
    storage.save()
    return jsonify({"message": "Deleted Successfully"}), 200
