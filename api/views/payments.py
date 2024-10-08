#!/usr/bin/python3
"""Payments Module"""

from api.views import app_views
from models import storage
from models.payments import Payments
from models.orders import Orders
from models.client import Client
from flask import jsonify, abort, request, make_response


@app_views.route('/clients/<client_id>/payments',
                 methods=['GET'], strict_slashes=False)
def get_client_payments(client_id):
    """Retrieve all payments from a specific client"""
    all_payments = storage.all(Payments).values()
    list_payments = [payment.to_dict() for
                     payment in all_payments if payment.client_id == client_id]
    return jsonify(list_payments)


@app_views.route('/orders/<order_id>/payments',
                 methods=['GET'], strict_slashes=False)
def get_order_payments(order_id):
    """Retrieve all payments from a specific order"""
    all_payments = storage.all(Payments).values()
    list_payments = [payment.to_dict() for
                     payment in all_payments if payment.order_id == order_id]
    return jsonify(list_payments)


@app_views.route('/payments/<payment_id>',
                 methods=['GET'], strict_slashes=False)
def get_payment(payment_id):
    """Retrieve a specific payment"""
    payment = storage.get(Payments, payment_id)
    if not payment:
        abort(404, description="Payment not found")
    return jsonify(payment.to_dict())


@app_views.route('/payments',
                 methods=['POST'], strict_slashes=False)
def add_payment():
    """Create a new payment"""
    if not request.get_json():
        abort(400, description="Not a valid JSON")
    required_fields = ['client_id', 'order_id', 'amount_paid', 'status']
    data = request.get_json()

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


@app_views.route('/payments/<payment_id>',
                 methods=['PUT'], strict_slashes=False)
def update_payment(payment_id):
    """Update an existing payment"""
    if not request.get_json():
        abort(400, description="Not a valid JSON")
    ignored_fields = ['id', 'created_at', 'updated_at']

    payment = storage.get(Payments, payment_id)
    if not payment:
        abort(404, description="Payment not found")
    data = request.get_json()

    for key, value in data.items():
        if key not in ignored_fields:
            setattr(payment, key, value)
    storage.save()
    return make_response(jsonify(payment.to_dict()), 200)


@app_views.route('/payments/<payment_id>',
                 methods=['DELETE'], strict_slashes=False)
def delete_payment(payment_id):
    """Delete a payment"""
    payment = storage.get(Payments, payment_id)
    if not payment:
        abort(404, description="Payment not found")
    storage.delete(payment)
    storage.save()
    return make_response(jsonify({}), 200)
