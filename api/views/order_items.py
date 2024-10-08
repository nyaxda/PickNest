#!/usr/bin/python3
"""OrderItems Module"""

from api.views import app_views
from models import storage
from models.order_items import OrderItems
from flask import jsonify, abort, request, make_response


@app_views.route('/orders/<order_id>/order_items',
                 methods=['GET'], strict_slashes=False)
def get_order_items(order_id):
    """Retrieve all order items for a specific order"""
    all_order_items = storage.all(OrderItems).values()
    list_items = [item.to_dict() for
                  item in all_order_items if
                  item.order_id == order_id]
    return jsonify(list_items)


@app_views.route('/orders/<order_id>/order_items/<item_id>',
                 methods=['GET'], strict_slashes=False)
def get_order_item(order_id, item_id):
    """Retrieve a specific order item"""
    order_item = storage.get(OrderItems, item_id)
    if not order_item or order_item.order_id != order_id:
        abort(404, description="Order item not found")
    return jsonify(order_item.to_dict())


@app_views.route('/orders/<order_id>/order_items',
                 methods=['POST'], strict_slashes=False)
def add_order_item(order_id):
    """Create a new order item"""
    if not request.get_json():
        abort(400, description="Not a valid JSON")
    required_fields = ['item_id', 'quantity_ordered', 'price_at_order_time']
    data = request.get_json()
    for field in required_fields:
        if field not in data:
            abort(400, description=f"{field} is missing")
    data['order_id'] = order_id
    instance = OrderItems(**data)
    instance.save()
    return make_response(jsonify(instance.to_dict()), 201)


@app_views.route('/orders/<order_id>/order_items/<item_id>',
                 methods=['PUT'], strict_slashes=False)
def update_order_item(order_id, item_id):
    """Update an existing order item"""
    if not request.get_json():
        abort(400, description="Not a valid JSON")
    ignored_fields = ['id', 'created_at', 'updated_at', 'order_id']

    order_item = storage.get(OrderItems, item_id)
    if not order_item or order_item.order_id != order_id:
        abort(404, description="Order item not found")
    data = request.get_json()
    for key, value in data.items():
        if key not in ignored_fields:
            setattr(order_item, key, value)
    storage.save()
    return make_response(jsonify(order_item.to_dict()), 200)


@app_views.route('/orders/<order_id>/order_items/<item_id>',
                 methods=['DELETE'], strict_slashes=False)
def delete_order_item(order_id, item_id):
    """Delete an order item"""
    order_item = storage.get(OrderItems, item_id)
    if not order_item or order_item.order_id != order_id:
        abort(404, description="Order item not found")
    storage.delete(order_item)
    storage.save()
    return make_response(jsonify({}), 200)
