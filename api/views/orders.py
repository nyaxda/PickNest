#!/usr/bin/python3
"""Orders Module"""

from api.views import app_views
from models import storage
from models.orders import Orders
from flask import jsonify, abort, request, make_response


@app_views.route('/orders', methods=['GET'], strict_slashes=False)
def get_orders():
    """Retrieve list of all orders"""
    all_orders = storage.all(Orders).values()
    list_orders = [order.to_dict() for order in all_orders]
    return jsonify(list_orders)


@app_views.route('/orders/<order_id>', methods=['GET'], strict_slashes=False)
def get_order(order_id):
    """Retrieve a specific order"""
    order = storage.get(Orders, order_id)
    if not order:
        abort(404, description="Order not found")
    return jsonify(order.to_dict())


@app_views.route('/orders', methods=['POST'], strict_slashes=False)
def add_order():
    """Create a new order"""
    if not request.get_json():
        abort(400, description="Not a valid JSON")
    required_fields = ['client_id', 'shipping_address_id', 'status']
    data = request.get_json()

    for field in required_fields:
        if field not in data:
            abort(400, description=f"{field} is missing")

    # Check if client and address exist
    client = storage.get(Client, data['client_id'])
    address = storage.get(Address, data['shipping_address_id'])

    if not client:
        abort(400, description="Client not found")
    if not address:
        abort(400, description="Address not found")

    instance = Orders(**data)
    instance.save()
    return make_response(jsonify(instance.to_dict()), 201)


@app_views.route('/orders/<order_id>', methods=['PUT'], strict_slashes=False)
def update_order(order_id):
    """Update an existing order"""
    if not request.get_json():
        abort(400, description="Not a valid JSON")
    ignored_fields = ['id', 'created_at', 'updated_at']

    order = storage.get(Orders, order_id)
    if not order:
        abort(404, description="Order not found")
    data = request.get_json()

    for key, value in data.items():
        if key not in ignored_fields:
            setattr(order, key, value)
    storage.save()
    return make_response(jsonify(order.to_dict()), 200)


@app_views.route('/orders/<order_id>',
                 methods=['DELETE'], strict_slashes=False)
def delete_order(order_id):
    """Delete an order"""
    order = storage.get(Orders, order_id)
    if not order:
        abort(404, description="Order not found")
    storage.delete(order)
    storage.save()
    return make_response(jsonify({}), 200)
