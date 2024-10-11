#!/usr/bin/python3
"""Payments Module"""

from api.views import app_views
from models import storage
from models.payments import Payments
from models.orders import Orders
from models.client import Client
from flask import jsonify, abort, request, make_response
from .token_auth import token_required
roles = ['client', 'admin']


@token_required
@app_views.route('/clients/<client_id>/payments',
                 methods=['GET'], strict_slashes=False)
def get_client_payments(current_user, client_id):
    """Retrieve all payments from a specific client"""
    if current_user.role not in roles:
        return jsonify({'Error': 'Invalid role'}), 403

    if current_user.role == 'client' and current_user.id != client_id:
         return jsonify({'Error': 'Invalid access'}), 403

    all_payments = storage.all(Payments).values()
    list_payments = [payment.to_dict() for
                     payment in all_payments if payment.client_id == client_id]
    return jsonify(list_payments)


@token_required
@app_views.route('/orders/<order_id>/payments',
                 methods=['GET'], strict_slashes=False)
def get_order_payments(current_user, order_id):
    """Retrieve all payments from a specific order"""
    if current_user.role not in roles:
        return jsonify({'Error': 'Invalid role'}), 403

    if current_user.role == 'client' and current_user.id != client_id:  # revisit
         return jsonify({'Error': 'Invalid access'}), 403
    
    all_payments = storage.all(Payments).values()
    list_payments = [payment.to_dict() for
                     payment in all_payments if payment.order_id == order_id]
    return jsonify(list_payments)


@token_required
@app_views.route('/payments/<payment_id>',
                 methods=['GET'], strict_slashes=False)
def get_payment(current_user, payment_id):
    """Retrieve a specific payment"""
    if current_user.role not in roles:
        return jsonify({'Error': 'Invalid role'}), 403

    payment = storage.get(Payments, payment_id)
    if not payment:
        abort(404, description="Payment not found")

    # restricts to ensure each user services his orders alone
    client = payment.order.client
    if current_user.role == 'client' and current_user.id != client.id:
         return jsonify({'Error': 'Invalid access'}), 403

    return jsonify(payment.to_dict())


@token_required
@app_views.route('/payments',
                 methods=['POST'], strict_slashes=False)
def add_payment(current_user):
    """Create a new payment"""
    if current_user.role not in roles:
        return jsonify({'Error': 'Invalid role'}), 403

    data = request.get_json()
    if not data:
        abort(400, description="Not a valid JSON")

    required_fields = ['client_id', 'order_id', 'amount_paid', 'status']

    if current_user.role == 'client' and current_user.id != data.get('client.id'):
         return jsonify({'Error': 'Invalid access'}), 403

    for field in required_fields:
        if field not in data:
            abort(400, description=f"{field} is missing")

    # Check if client and order exist
    client = storage.get(Client, data['client_id'])
    order = storage.get(Orders, data['order_id'])

    if not client:
        abort(400, description="Client not found")
    if not order:
        abort(400, description="Order not found")

    instance = Payments(**data)
    instance.save()
    return make_response(jsonify(instance.to_dict()), 201)


@token_required
@app_views.route('/payments/<payment_id>',
                 methods=['PUT'], strict_slashes=False)
def update_payment(current_user, payment_id):
    """Update an existing payment"""
    if current_user.role not in roles:
        return jsonify({'Error': 'Invalid role'}), 403

    data = request.get_json()
    if not data:
        abort(400, description="Not a valid JSON")

    ignored_fields = ['id', 'created_at', 'updated_at']

    payment = storage.get(Payments, payment_id)
    if not payment:
        abort(404, description="Payment not found")

    # restricts to ensure each user services his orders alone
    client = payment.order.client
    if current_user.role == 'client' and current_user.id != client.id:
         return jsonify({'Error': 'Invalid access'}), 403

    for key, value in data.items():
        if key not in ignored_fields:
            setattr(payment, key, value)
    storage.save()
    return make_response(jsonify(payment.to_dict()), 200)


@token_required
@app_views.route('/payments/<payment_id>',
                 methods=['DELETE'], strict_slashes=False)
def delete_payment(current_user, payment_id):
    """Delete a payment"""
    if current_user.role not in roles:
        return jsonify({'Error': 'Invalid role'}), 403

    payment = storage.get(Payments, payment_id)
    if not payment:
        abort(404, description="Payment not found")

    # restricts to ensure each user services his orders alone
    client = payment.order.client
    if current_user.role == 'client' and current_user.id != client.id:
         return jsonify({'Error': 'Invalid access'}), 403

    storage.delete(payment)
    storage.save()
    return make_response(jsonify({}), 200)
