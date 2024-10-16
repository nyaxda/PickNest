#!/usr/bin/python3
"""OrderItems Module"""

from api.views import app_views
from models import storage
from models.order_items import OrderItems
from models.items import Items
from flask import jsonify, request
from models.orders import Orders
from sqlalchemy.exc import IntegrityError
from .token_auth import token_required
import uuid

roles = ["admin", "client"]


@app_views.route('/orders/<order_id>/order_items',
                 methods=['GET'], strict_slashes=False)
@token_required
def get_order_items(current_user, order_id):
    """Retrieve all order items for a specific order"""
    if current_user.role not in roles:
        return jsonify({'Error': 'Invalid role'})

    all_order_items = storage.all(OrderItems)
    list_items = [item.to_dict() for
                  item in all_order_items if
                  item.order_id == order_id]
    return jsonify(list_items)


@app_views.route('/orders/<order_id>/order_items/<order_item_id>',
                 methods=['GET'], strict_slashes=False)
@token_required
def get_order_item(current_user, order_id, order_item_id):
    """Retrieve a specific order item"""
    if current_user.role not in roles:
        return jsonify({'Error': 'Invalid role'}), 403
    order_item = storage.get(OrderItems, order_item_id)
    if not order_item or order_item.order_id != order_id:
        return jsonify({"Error": "Order item not found"})
    return jsonify(order_item.to_dict())


@app_views.route('/orders/<order_id>/order_items',
                 methods=['POST'], strict_slashes=False)
@token_required
def add_order_item(current_user, order_id):
    """Create a new order item"""
    if current_user.role not in roles:
        return jsonify({'Error': 'Invalid role'}), 403
    data = request.get_json()
    if not data:
        return jsonify({"Error": "Not a valid JSON"}), 400
    required_fields = ['item_id', 'quantity_ordered']
    for field in required_fields:
        if field not in data:
            return jsonify({"Error": f"{field} is required"}), 400

    item = storage.get(Items, data['item_id'])
    if not item:
        return jsonify({"Error": "Item not found"}), 404

    # Check if the item_id already exists in the order_id
    order_items = storage.all(OrderItems)
    existing_order_item = next((oi for oi in order_items if
                                oi.order_id == order_id and
                                oi.item_id == data['item_id']), None)
    if existing_order_item:
        return jsonify({"Error": "Item already exists in the order"}), 400

    if data['quantity_ordered'] > item.initial_stock:
        return jsonify({"Error": "Insufficient stock"}), 400
    price_at_order_time = item.price * data['quantity_ordered']

    order_item = OrderItems(
        public_id=str(uuid.uuid4()),
        order_id=order_id,
        item_id=data['item_id'],
        quantity_ordered=data['quantity_ordered'],
        price_at_order_time=price_at_order_time
    )
    # Retrieve the existing order
    order = storage.get(Orders, order_id)
    if not order:
        return jsonify({"Error": "Order not found"})

    # Calculate the new order total
    new_order_total = order.order_total + price_at_order_time
    order.order_total = new_order_total

    try:
        storage.new(order_item)
        storage.save()

        # Update the item's initial stock
        new_initial_stock = item.initial_stock - data['quantity_ordered']
        item.initial_stock = new_initial_stock

        # Save the updated item
        storage.save()

        return jsonify(order_item.to_dict()), 201

    except IntegrityError as e:
        if 'check_quantity_ordered_gt0' in str(e.orig):
            return jsonify({
                'Error': 'Quantity ordered should be 1 or more'}), 400
        return jsonify({'Error': 'Invalid data', 'message': str(e.orig)}), 400


@app_views.route('/orders/<order_id>/order_items/<order_item_id>',
                 methods=['PUT'], strict_slashes=False)
@token_required
def update_order_item(current_user, order_id, order_item_id):
    """Update an existing order item"""
    if current_user.role not in roles:
        return jsonify({'Error': 'Invalid role'})
    if not request.get_json():
        return jsonify({"Error": "Not a valid JSON"}), 400
    ignored_fields = ['public_id', 'created_at', 'updated_at',
                      'order_id', 'price_at_order_time']
    data = request.get_json()
    order_item = storage.get(OrderItems, order_item_id)
    if not order_item or order_item.order_id != order_id:
        return jsonify({"Error": "Order item not found"}), 404
    item = storage.get(Items, order_item.item_id)
    if not item:
        return jsonify({"Error": "Item not found"}), 404
    if data and 'quantity_ordered' in data and \
            data['quantity_ordered'] > item.initial_stock:
        return jsonify({"Error": "Insufficient stock"}), 400
    new_quantity = data.get('quantity_ordered', order_item.quantity_ordered)
    old_quantity = order_item.quantity_ordered
    price_per_item = order_item.price_at_order_time / old_quantity

    if new_quantity > old_quantity:
        # Deduct the difference from the stock
        stock_difference = new_quantity - old_quantity
        if stock_difference > item.initial_stock:
            return jsonify({"Error": "Insufficient stock"}), 400
        new_stock = item.initial_stock - stock_difference
        item.initial_stock = new_stock

    elif new_quantity < old_quantity:
        # Restock the difference
        stock_difference = old_quantity - new_quantity
        new_stock = item.initial_stock + stock_difference
        item.initial_stock = new_stock

    # Calculate the new price at order time
    new_price_at_order_time = price_per_item * new_quantity

    # Retrieve the existing order
    order = storage.get(Orders, order_id)
    if not order:
        return jsonify({"Error": "Order not found"}), 404

    # Calculate the new order total
    order.order_total = order.order_total - order_item.price_at_order_time \
        + new_price_at_order_time

    for key, value in data.items():
        if key not in ignored_fields:
            setattr(order_item, key, value)
    try:
        storage.save()
        return jsonify(order_item.to_dict()), 200
    except IntegrityError as e:
        if 'check_quantity_ordered_gt0' in str(e.orig):
            return jsonify({
                'Error': 'Quantity ordered should be 1 or more'}), 400
        return jsonify({'Error': 'Invalid data', 'message': str(e.orig)}), 400


@app_views.route('/orders/<order_id>/order_items/<item_id>',
                 methods=['DELETE'], strict_slashes=False)
@token_required
def delete_order_item(current_user, order_id, item_id):
    """Delete an order item"""
    if current_user.role not in roles:
        return jsonify({'Error': 'Invalid role'})
    order_item = storage.get(OrderItems, item_id)
    if not order_item or order_item.order_id != order_id:
        return jsonify({"Error": "Order item not found"}), 404

    order = storage.get(Orders, order_id)
    if not order:
        return jsonify({"Error": "Order not found"}), 404

    item = storage.get(Items, order_item.item_id)
    if not item:
        return jsonify({"Error": "Item not found"}), 404
    if order.status == 'Pending':
        new_stock = item.initial_stock + order_item.quantity_ordered
        item.initial_stock = new_stock
    try:
        storage.delete(order_item)
        storage.save()
        return jsonify({
            "message":
            f"Deleted Order Item {order_item.public_id} successfully"}), 200
    except IntegrityError as e:
        return jsonify({
            "Error": f"An error occurred during deletion : {str(e)}"}), 400
