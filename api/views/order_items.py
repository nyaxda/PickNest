#!/usr/bin/python3
"""OrderItems Module"""

from api.views import app_views
from models import storage
from models.order_items import OrderItems
from models.items import Items
from flask import jsonify, abort, request, make_response
from .token_auth import token_required
roles = ['admin', 'client']


@token_required
@app_views.route('/orders/<order_id>/order_items',
                 methods=['GET'], strict_slashes=False)
def get_order_items(current_user, order_id):
    """Retrieve all order items for a specific order"""
    if current_user not in roles:
        return jsonify({'Error': 'Invalid role'})

    all_order_items = storage.all(OrderItems).values()
    list_items = [item.to_dict() for
                  item in all_order_items if
                  item.order_id == order_id]
    return jsonify(list_items)


@token_required
@app_views.route('/orders/<order_id>/order_items/<item_id>',
                 methods=['GET'], strict_slashes=False)
def get_order_item(current_user, order_id, item_id):
    """Retrieve a specific order item"""
    order_item = storage.get(OrderItems, item_id)
    if not order_item or order_item.order_id != order_id:
        abort(404, description="Order item not found")
    return jsonify(order_item.to_dict())


@token_required
@app_views.route('/orders/<order_id>/order_items',
                 methods=['POST'], strict_slashes=False)
def add_order_item(current_user, order_id):
    """Create a new order item"""
    if not request.get_json():
        abort(400, description="Not a valid JSON")
    required_fields = ['item_id', 'quantity_ordered', 'price_at_order_time']
    data = request.get_json()
    for field in required_fields:
        if field not in data:
            abort(400, description=f"{field} is missing")
    item = storage.get(Items, data['item_id'])
    if not item:
        abort(404, description="Item not found")

    try:
        item.update_stock(data['quantity_ordered'])
    except ValueError as e:
        abort(400, description=str(e))

    data['order_id'] = order_id
    instance = OrderItems(**data)
    instance.save()
    return make_response(jsonify(instance.to_dict()), 201)


@token_required
@app_views.route('/orders/<order_id>/order_items/<item_id>',
                 methods=['PUT'], strict_slashes=False)
def update_order_item(current_user, order_id, item_id):
    """Update an existing order item"""
    if not request.get_json():
        abort(400, description="Not a valid JSON")
    ignored_fields = ['id', 'created_at', 'updated_at', 'order_id']

    order_item = storage.get(OrderItems, item_id)
    if not order_item or order_item.order_id != order_id:
        abort(404, description="Order item not found")
    item = storage.get(Items, order_item.item_id)
    if not item:
        abort(404, description="Item not found")
    # Calculate the stock based on new quantity
    new_quantity = request.get_json().get('quantity_ordered',
                                          order_item.quantity_ordered)
    old_quantity = order_item.quantity_ordered
    if new_quantity > old_quantity:
        # need to deduct difference from the stock
        try:
            item.update_stock(new_quantity - old_quantity)
        except ValueError as e:
            abort(400, description=str(e))

    elif new_quantity < old_quantity:
        # Restock the difference:
        item.restock(old_quantity - new_quantity)

    data = request.get_json()
    for key, value in data.items():
        if key not in ignored_fields:
            setattr(order_item, key, value)
    storage.save()
    return make_response(jsonify(order_item.to_dict()), 200)


@token_required
@app_views.route('/orders/<order_id>/order_items/<item_id>',
                 methods=['DELETE'], strict_slashes=False)
def delete_order_item(current_user, order_id, item_id):
    """Delete an order item"""
    order_item = storage.get(OrderItems, item_id)
    if not order_item or order_item.order_id != order_id:
        abort(404, description="Order item not found")

    item = storage.get(Items, order_item.item_id)
    if item:
        item.restock(order_item.quantity_ordered)

    storage.delete(order_item)
    storage.save()
    return make_response(jsonify({}), 200)
