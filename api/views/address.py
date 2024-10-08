#!/usr/bin/python3
"""Address Module"""

from api.views import app_views
from models import storage
from models.address import Address
from flask import jsonify, abort, request, make_response


@app_views.route('/clients/<client_id>/addresses',
                 methods=['GET'], strict_slashes=False)
def get_client_addresses(client_id):
    """Retrieve all addresses for a specific client"""
    all_addresses = storage.all(Address).values()
    list_addresses = [address.to_dict() for
                      address in all_addresses if
                      address.client_id == client_id]
    return jsonify(list_addresses)


@app_views.route('/addresses/<address_id>',
                 methods=['GET'], strict_slashes=False)
def get_address(address_id):
    """Retrieve a specific address"""
    address = storage.get(Address, address_id)
    if not address:
        abort(404, description="Address not found")
    return jsonify(address.to_dict())


@app_views.route('/addresses',
                 methods=['POST'], strict_slashes=False)
def add_address():
    """Create a new address"""
    if not request.get_json():
        abort(400, description="Not a valid JSON")
    required_fields = ['client_id',
                       'address_line1', 'city',
                       'state', 'postal_code', 'country']
    data = request.get_json()
    for field in required_fields:
        if field not in data:
            abort(400, description=f"{field} is missing")
    instance = Address(**data)
    instance.save()
    return make_response(jsonify(instance.to_dict()), 201)


@app_views.route('/addresses/<address_id>',
                 methods=['PUT'], strict_slashes=False)
def update_address(address_id):
    """Update an existing address"""
    if not request.get_json():
        abort(400, description="Not a valid JSON")
    ignored_fields = ['id', 'created_at', 'updated_at']

    address = storage.get(Address, address_id)
    if not address:
        abort(404, description="Address not found")
    data = request.get_json()
    for key, value in data.items():
        if key not in ignored_fields:
            setattr(address, key, value)
    storage.save()
    return make_response(jsonify(address.to_dict()), 200)


@app_views.route('/addresses/<address_id>',
                 methods=['DELETE'], strict_slashes=False)
def delete_address(address_id):
    """Delete an address"""
    address = storage.get(Address, address_id)
    if not address:
        abort(404, description="Address not found")
    storage.delete(address)
    storage.save()
    return make_response(jsonify({}), 200)
