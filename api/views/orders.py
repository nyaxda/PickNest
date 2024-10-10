#!/usr/bin/python3
"""Orders Module"""

from api.views import app_views
from models import storage
from models.orders import Orders
from flask import jsonify, abort, request, make_response
from .token_auth import token_required


@token_required
@app_views.route('/orders', methods=['GET'], strict_slashes=False)
def get_orders(current_user):
    """Retrieve list of all orders"""
    roles = ['admin']
    if current_user.role not in roles:
        jsonify({'Error': 'Invalid access'}), 403

    all_orders = storage.all(Orders).values()
    list_orders = [order.to_dict() for order in all_orders]
    return jsonify(list_orders)


@token_required
@app_views.route('/orders/<order_id>', methods=['GET'], strict_slashes=False)
def get_order(current_user, order_id):
    """Retrieve a specific order"""
    roles = ['admin', 'client']
    if current_user.role not in roles:
        jsonify({'Error': 'Invalid access'}), 403

    order = storage.get(Orders, order_id)
    if not order:
        abort(404, description="Order not found")

    # restrict clients accessing other client orders
    if current_user.role == 'client' and current_user.id != order.client_id:
        return jsonify({'Error': 'Invalid access'}), 403

    return jsonify(order.to_dict())


@token_required
@app_views.route('/orders', methods=['POST'], strict_slashes=False)
def add_order(current_user):
    """Create a new order"""
    roles = ['admin', 'client']
    if current_user.role not in roles:
        jsonify({'Error': 'Invalid access'}), 403

    data = request.get_json()
    if not data:
        abort(400, description="Not a valid JSON")

    # Check if client and address exist
    client = storage.get(Client, data['client_id'])
    address = storage.get(Address, data['shipping_address_id'])

    if not client:
        abort(400, description="Client not found")
    if not address:
        abort(400, description="Address not found")

    # restrict unrestricted user access
    if current_user.role == 'client' and current_user.id != data.get('client_id'):
        jsonify({'Error': 'Invalid access'}), 403

    required_fields = ['client_id', 'shipping_address_id', 'status']

    for field in required_fields:
        if field not in data:
            abort(400, description=f"{field} is missing")

    instance = Orders(**data)
    instance.save()
    return make_response(jsonify(instance.to_dict()), 201)


@token_required
@app_views.route('/orders/<order_id>', methods=['PUT'], strict_slashes=False)
def update_order(current_user, order_id):
    """Update an existing order"""
    roles = ['admin', 'client']
    if current_user.role not in roles:
        jsonify({'Error': 'Invalid access'}), 403

    data = request.get_json()
    if not data:
        abort(400, description="Not a valid JSON")

    ignored_fields = ['id', 'created_at', 'updated_at']

    order = storage.get(Orders, order_id)
    if not order:
        abort(404, description="Order not found")

    # restrict unrestricted user access
    if current_user.role == 'client' and current_user.id != order.client_id:
        jsonify({'Error': 'Invalid access'}), 403

    for key, value in data.items():
        if key not in ignored_fields:
            setattr(order, key, value)
    storage.save()
    return make_response(jsonify(order.to_dict()), 200)


@token_required
@app_views.route('/orders/<order_id>',
                 methods=['DELETE'], strict_slashes=False)
def delete_order(current_user, order_id):
    """Delete an order"""
    roles = ['admin', 'client']
    if current_user.role not in roles:
        jsonify({'Error': 'Invalid access'}), 403

    order = storage.get(Orders, order_id)
    if not order:
        abort(404, description="Order not found")

    # restrict unrestricted user access
    if current_user.role == 'client' and current_user.id != order.client_id:
        jsonify({'Error': 'Invalid access'}), 403

    storage.delete(order)
    storage.save()
    return make_response(jsonify({}), 200)
