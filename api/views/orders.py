#!/usr/bin/python3
"""Orders Module"""

from api.views import app_views
from models import storage
from models.orders import Orders
from models.client import Client
from models.address import Address
from flask import jsonify, request
from sqlalchemy.exc import IntegrityError
from .token_auth import token_required
import uuid

roles = ['admin', 'client']

@app_views.route('/orders', methods=['GET'], strict_slashes=False)
@token_required
def get_all_orders(current_user):
    """Retrieve list of all orders"""
    role = ['admin']
    if current_user.role not in role:
        return jsonify({'Error': 'Invalid access'}), 403

    all_orders = storage.all(Orders)
    list_orders = [order.to_dict() for order in all_orders]
    return jsonify(list_orders)

@app_views.route('/clients/<client_id>/orders',
                 methods=['GET'], strict_slashes=False)
@token_required
def get_client_orders(current_user, client_id):
    """Retrieve all items from a specific company"""
    if current_user.role not in roles:
        return jsonify({'Error': 'Invalid access'}), 403

    # restricts companies from accessing other companies' profiles
    if current_user.role == 'client' and current_user.public_id != client_id:
        return jsonify({'Error': 'Invalid access'}), 403

    all_orders = storage.all(Orders)
    list_orders = [order.to_dict() for
                  order in all_orders if order.client_id == client_id]
    return jsonify(list_orders)

@app_views.route('/orders/<order_id>', methods=['GET'], strict_slashes=False)
@token_required
def get_order(current_user, order_id):
    """Retrieve a specific order"""
    roles = ['admin', 'client']
    if current_user.role not in roles:
        jsonify({'Error': 'Invalid access'}), 403

    order = storage.get(Orders, order_id)
    if not order:
        return jsonify({"Error": "Order not found"}), 404

    # restrict clients accessing other client orders
    if current_user.role == 'client' and current_user.public_id != order.client_id:
        return jsonify({'Error': 'Invalid access'}), 403

    return jsonify(order.to_dict())


@app_views.route('/orders', methods=['POST'], strict_slashes=False)
@token_required
def add_order(current_user):
    """Create a new order"""
    roles = ['admin', 'client']
    if current_user.role not in roles:
        return jsonify({'Error': 'Invalid access'}), 403

    data = request.get_json()
    if not data:
        return jsonify({"Error": "Not a valid JSON"}), 400
    required_fields = ['client_id', 'shipping_address_id']

    for field in required_fields:
        if field not in data:
            return jsonify({"Error": f"{field} is required"}), 400

    # Check if client and address exist
    client = storage.get(Client, data['client_id'])
    address = storage.get(Address, data['shipping_address_id'])

    # confirm if address is associated with the client through client_id foreign key in address table
    if address and client.public_id != address.client_id:
        return jsonify({"Error": "Address not associated with client"}), 400

    if not client:
        return jsonify({"Error": "Client not found"}), 400
    if not address:
        return jsonify({"Error": "Address not found"}), 400

    # restrict unrestricted user access
    if current_user.role == 'client' and current_user.public_id != data.get('client_id'):
        return jsonify({'Error': 'Invalid access'}), 403
    
    # Ensure order_total is not set or modified
    if 'order_total' in data:
        return jsonify({"Error": "Order total cannot be set manually"}), 400

    data['status'] = 'pending'
    data["public_id"] = str(uuid.uuid4())

    instance = Orders(**data)
    try:
        storage.new(instance)
        storage.save()
    except IntegrityError as e:
        if 'status' in str(e.orig):
            return jsonify({
                "Error":
                "Invalid status value. Valid values are Pending, Shipped, Delivered, Cancelled"
            }), 400
        return jsonify({'Error': 'Integrity error occurred', 'Message': str(e)}), 400

    return jsonify(instance.to_dict()), 201


@app_views.route('/orders/<order_id>', methods=['PUT'], strict_slashes=False)
@token_required
def update_order(current_user, order_id):
    """Update an existing order"""
    roles = ['admin', 'client']
    if current_user.role not in roles:
        return jsonify({'Error': 'Invalid access'}), 403

    data = request.get_json()
    if not data:
        return jsonify({"Error": "Not a valid JSON"}), 400

    order = storage.get(Orders, order_id)
    if not order:
        return jsonify({"Error": "Order not found"}), 404

    # restrict unrestricted user access
    if current_user.role == 'client' and current_user.public_id != order.client_id:
        return jsonify({'Error': 'Invalid access'}), 403

    ignored_fields = ['id', 'created_at', 'updated_at', 'client_id', 'order_total']

    for key, value in data.items():
        if key in ignored_fields:
            return jsonify({"Error": f"{key} cannot be modified"}), 400
        elif key == 'shipping_address_id':
            # Ensure the related address exists and is linked to the client
            address = storage.get(Address, value)
            if not address or address.client_id != order.client_id:
                return jsonify({"Error": "Invalid shipping_address_id"}), 400
            setattr(order, key, value)
        elif key == 'status':
            if value not in ['Pending', 'Shipped', 'Delivered', 'Cancelled']:
                return jsonify({"Error": "Invalid status value"}), 400
            setattr(order, key, value)
        else:
            return jsonify({"Error": f"Invalid attribute {key}"}), 400
  
    try:
        storage.save()
    except IntegrityError as e:
        return jsonify({'Error': 'Invalid data', 'message': str(e)})

    return jsonify(order.to_dict()), 200


@app_views.route('/orders/<order_id>',
                 methods=['DELETE'], strict_slashes=False)
@token_required
def delete_order(current_user, order_id):
    """Delete an order"""
    roles = ['admin', 'client']
    if current_user.role not in roles:
        return jsonify({'Error': 'Invalid access'}), 403

    order = storage.get(Orders, order_id)
    if not order:
        return jsonify({"Error": "Order not found"}), 404

    # restrict unrestricted user access
    if current_user.role == 'client' and current_user.public_id != order.client_id:
        return jsonify({'Error': 'Invalid access'}), 403
    try:
        storage.delete(order)
        storage.save()
        return jsonify({"message": f"Deleted Order {order.public_id} successfully"}), 200
    except IntegrityError as e:
        return jsonify({"Error": f"An error occurred during deletion : {str(e)}"}), 400
