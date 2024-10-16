#!/usr/bin/python3
"""Payments Module"""

from api.views import app_views
from models import storage
from models.payments import Payments
from models.orders import Orders
from models.client import Client
from models.items import Items
from flask import jsonify, request
from sqlalchemy.exc import IntegrityError
from datetime import datetime
import uuid
from .token_auth import token_required
roles = ['client', 'admin']


@app_views.route('/clients/<client_id>/payments',
                 methods=['GET'], strict_slashes=False)
@token_required
def get_client_payments(current_user, client_id):
    """Retrieve all payments from a specific client"""
    if current_user.role not in roles:
        return jsonify({'Error': 'Invalid role'}), 403

    if current_user.role == 'client' and current_user.public_id != client_id:
         return jsonify({'Error': 'Invalid access'}), 403

    # Retrieve all orders for the specified client
    all_orders = storage.all(Orders)
    client_orders = [order.public_id for order in all_orders if order.client_id == client_id]

    # Retrieve all payments for the client's orders
    all_payments = storage.all(Payments)
    list_payments = [payment.to_dict() for payment in all_payments if payment.order_id in client_orders]
    return jsonify(list_payments)


@app_views.route('/payments', methods=['GET'], strict_slashes=False)
@token_required
def get_all_payments(current_user):
    """Retrieve all payments as admin"""
    if current_user.role != 'admin':
        return jsonify({'Error': 'Invalid role'}), 403

    all_payments = storage.all(Payments)
    list_payments = [payment.to_dict() for payment in all_payments]
    return jsonify(list_payments)

@app_views.route('/orders/<order_id>/payments',
                 methods=['GET'], strict_slashes=False)
@token_required
def get_order_payments(current_user, order_id):
    """Retrieve all payments from a specific order"""
    if current_user.role not in roles:
        return jsonify({'Error': 'Invalid role'}), 403

    order = storage.get(Orders, order_id)
    if not order:
        return jsonify({'Error': 'Order not found'}), 404

    if current_user.role == 'client' and current_user.public_id != order.client_id:
         return jsonify({'Error': 'Invalid access'}), 403
    
    all_payments = storage.all(Payments)
    list_payments = [payment.to_dict() for
                     payment in all_payments if payment.order_id == order_id]
    return jsonify(list_payments)



@app_views.route('/payments/<payment_id>',
                 methods=['GET'], strict_slashes=False)
@token_required
def get_payment(current_user, payment_id):
    """Retrieve a specific payment"""
    if current_user.role not in roles:
        return jsonify({'Error': 'Invalid role'}), 403

    payment = storage.get(Payments, payment_id)
    if not payment:
        return jsonify({'Error': 'Payment not found'}), 404

    order_id = payment.order_id
    order = storage.get(Orders, order_id)
    if not order:
        return jsonify({'Error': 'Order not found'}), 404
    # restricts to ensure each user services his orders alone
    client_id = order.client_id

    if current_user.role == 'client' and current_user.public_id != client_id:
         return jsonify({'Error': 'Invalid access'}), 403

    return jsonify(payment.to_dict())



@app_views.route('/payments',
                 methods=['POST'], strict_slashes=False)
@token_required
def add_payment(current_user):
    """Create a new payment"""
    if current_user.role not in roles:
        return jsonify({'Error': 'Invalid role'}), 403

    data = request.get_json()
    if not data:
        return jsonify({"Error": "Not a valid JSON"}), 400

    # Check if order exist
    order = storage.get(Orders, data['order_id'])
    if not order:
        return jsonify({'Error': 'Order not found'}), 404

    if current_user.role == 'client' and current_user.public_id != order.client_id:
         return jsonify({'Error': f'Invalid access {current_user.public_id} vs {order.client_id}'}), 403

    required_fields = ['order_id', 'amount_paid', 'transaction_reference_number']

    for field in required_fields:
        if field not in data:
            return jsonify({'Error': f'{field} is missing'}), 400

    amount_paid = data['amount_paid']
    if amount_paid < order.order_total:
        payment_status = 'Failed'
        order_status = 'Cancelled'
        # Restock items
        for order_item in order.order_items:
            item = storage.get(Items, order_item.item_id)
            if item:
                item.initial_stock += order_item.quantity_ordered
    else:
        payment_status = 'Completed'
        order_status = 'Shipped'

    # Validate payment method
    valid_payment_methods = ['Credit Card', 'PayPal', 'M-Pesa']
    if 'payment_method' not in data or data['payment_method'] not in valid_payment_methods:
        data['payment_method'] = 'Credit Card'
    if 'currency' not in data:
        data['currency'] = 'KES'

    instance = Payments(
        public_id = str(uuid.uuid4()),
        order_id=data['order_id'],
        amount_paid=amount_paid,
        status=payment_status,
        payment_method=data['payment_method'],
        transaction_reference_number=data['transaction_reference_number'],
        Currency=data['currency'],
        payment_date=datetime.utcnow()
    )

    order.status = order_status

    try:
        storage.new(instance)
        storage.save()
        return jsonify(instance.to_dict()), 201
    except IntegrityError as e:
        if 'payment_method' in str(e.orig):
            return jsonify({'Error': 'Invalid payment method'}), 400
        return jsonify({'Error': 'Invalid data', 'message': str(e.orig)}), 400



@app_views.route('/payments/<payment_id>',
                 methods=['PUT'], strict_slashes=False)
@token_required
def update_payment(current_user, payment_id):
    """Update an existing payment"""
    if current_user.role not in roles:
        return jsonify({'Error': 'Invalid role'}), 403

    data = request.get_json()
    if not data:
        return jsonify({'Error': 'Not a valid JSON'}), 400

    ignored_fields = ['id', 'created_at', 'updated_at', 'client_id', 'order_id', 'payment_date']

    payment = storage.get(Payments, payment_id)
    if not payment:
        return jsonify({'Error': 'Payment not found'}), 404

    # restricts to ensure each user services his orders alone
    order_id = payment.order_id

    # Retrieve the associated order
    order = storage.get(Orders, order_id)
    if not order:
        return jsonify({'Error': 'Order not found'}), 404
    # restricts to ensure each user services his orders alone
    client_id = order.client_id
    if current_user.role == 'client' and current_user.public_id != client_id:
         return jsonify({'Error': 'Invalid access'}), 403

    if order.status == 'Cancelled':
        return jsonify({'Error': 'Cannot update payment for a cancelled order'}), 400
    if order.status == 'Shipped':
        return jsonify({'Error': 'The order is already shipped'}), 400

    for key, value in data.items():
        if key not in ignored_fields:
            setattr(payment, key, value)
    
    # Update payment and order status if necessary
    if 'amount_paid' in data:
        amount_paid = data['amount_paid']
        if amount_paid < order.order_total:
            payment.status = 'Failed'
            order.status = 'Cancelled'
            # Restock items
            for order_item in order.order_items:
                item = storage.get(Items, order_item.item_id)
                if item:
                    new_stock = item.initial_stock + order_item.quantity_ordered
                    item.initial_stock = new_stock
                else:
                    payment.status = 'Completed'
                    order.status = 'Shipped'

    # Validate payment method if it is being updated
    if 'payment_method' in data:
        valid_payment_methods = ['Credit Card', 'PayPal', 'M-Pesa']
        if data['payment_method'] not in valid_payment_methods:
            return jsonify({'Error': 'Invalid payment method'}), 400

    try:
        storage.save()
        return jsonify(payment.to_dict()), 200
    except IntegrityError as e:
        if 'payment_method' in str(e.orig):
            return jsonify({'Error': 'Invalid payment method'}), 400
        return jsonify({'Error': 'Invalid data', 'message': str(e.orig)}), 400


@app_views.route('/payments/<payment_id>',
                 methods=['DELETE'], strict_slashes=False)
@token_required
def delete_payment(current_user, payment_id):
    """Delete a payment"""
    if current_user.role not in roles:
        return jsonify({'Error': 'Invalid role'}), 403

    payment = storage.get(Payments, payment_id)
    if not payment:
        return jsonify({'Error': 'Payment not found'}), 404

    # restricts to ensure each user services his orders alone
    client = payment.order.client
    if current_user.role == 'client' and current_user.public_id != client.id:
         return jsonify({'Error': 'Invalid access'}), 403

    # Check if the payment status is 'Pending'
    if payment.status == 'Completed':
        return jsonify({'Error': 'Completed payments cannot be deleted'}), 400

    # Retrieve the associated order
    order = storage.get(Orders, payment.order_id)
    if not order:
        return jsonify({'Error': 'Order not found'}), 404

    # Update order status to 'Cancelled'
    order.status = 'Cancelled'

    # Restock items
    for order_item in order.order_items:
        item = storage.get(Items, order_item.item_id)
        if item:
            new_stock = item.initial_stock + order_item.quantity_ordered
            item.initial_stock = new_stock
    
    try:
        # Delete the payment
        storage.delete(payment)
        storage.save()
        return jsonify({"message": f"Payment {payment.public_id} deleted successfully"}), 200
    except IntegrityError as e:
        return jsonify({'Error': 'Database error', 'message': str(e.orig)}), 400
