#!/usr/bin/python3
"""Items Module"""

from api.views import app_views
from models import storage
from models.items import Items
from flask import jsonify, request
from .token_auth import token_required
from sqlalchemy.exc import IntegrityError
import uuid

roles = ['admin', 'company']


@app_views.route('/companies/<company_id>/items',
                 methods=['GET'], strict_slashes=False)
@token_required
def get_company_items(current_user, company_id):
    """Retrieve all items from a specific company"""
    if current_user.role not in roles:
        return jsonify({'Error': 'Invalid access'}), 403

    # restricts companies from accessing other companies' profiles
    if current_user.role == 'company' and current_user.public_id != company_id:
        return jsonify({'Error': 'Invalid access'}), 403

    all_items = storage.all(Items)
    list_items = [item.to_dict() for
                  item in all_items if item.company_id == company_id]
    return jsonify(list_items)


@app_views.route('/items', methods=['GET'], strict_slashes=False)
@token_required
def get_all_items(current_user):
    """Retrieve all items, only accessible by admin"""
    if current_user.role != 'admin':
        return jsonify({'Error': 'Unauthorized access'}), 403

    all_items = storage.all(Items)
    list_items = [item.to_dict() for item in all_items]
    return jsonify(list_items)


@app_views.route('/items/<item_id>',
                 methods=['GET'], strict_slashes=False)
@token_required
def get_item(current_user, item_id):
    """Retrieve a specific item"""
    if current_user.role not in roles:
        return jsonify({'Error': 'Invalid access'}), 403

    item = storage.get(Items, item_id)
    if not item:
        return jsonify({'Error': 'Item not found'}), 404

    # restricts companies from accessing other companies' profiles
    if (current_user.role == 'company' and
            current_user.public_id != item.company_id):
        return jsonify({'Error': 'Invalid access'}), 403
    return jsonify(item.to_dict())


@app_views.route('/items',
                 methods=['POST'], strict_slashes=False)
@token_required
def add_item(current_user):
    """Create a new item"""
    if current_user.role not in roles:
        return jsonify({'Error': 'Invalid access'}), 403

    data = request.get_json()
    if not data:
        return jsonify({'Error': 'Not a valid JSON'}), 400

    # restricts companies from accessing other companies' profiles
    if (current_user.role == 'company' and
            current_user.public_id != data.get('company_id')):
        return jsonify({'Error': 'Invalid access'}), 403

    required_fields = ['company_id', 'name',
                       'stockamount', 'reorder_level',
                       'price', 'description', 'category', 'SKU']
    for field in required_fields:
        if field not in data:
            return jsonify({'Error': f'{field} is missing'}), 400
    # Calculate initial_stock based on stockamount
    data['initial_stock'] = data['stockamount']
    data["public_id"] = str(uuid.uuid4())

    instance = Items(**data)
    try:
        storage.new(instance)
        storage.save()
    except IntegrityError as e:
        if 'Duplicate' in str(e):
            return jsonify({'Error': 'Duplicate SKU'}), 400
        if 'check_stockamount_non_negative' in str(e.orig):
            return jsonify({'Error':
                            'Stock amount should be non-negative'}), 400
        if 'check_initial_stock_non_negative' in str(e.orig):
            return jsonify({'Error':
                            'Initial stock should be non-negative'}), 400
        if 'check_reorder_level_non_negative' in str(e.orig):
            return jsonify({'Error':
                            'Reorder level should be non-negative'}), 400
        return jsonify({'Error':
                        'Invalid data', 'message': str(e)}), 400
    return jsonify({"message": "Item Added Successfully"}), 201


@app_views.route('/items/<item_id>',
                 methods=['PUT'], strict_slashes=False)
@token_required
def update_item(current_user, item_id):
    """Update an existing item"""
    if current_user.role not in roles:
        return jsonify({'Error': 'Invalid access'}), 403

    data = request.get_json()
    if not data:
        return jsonify({'Error': 'Not a valid JSON'}), 400

    # restricts companies from accessing other companies' profiles
    if (current_user.role == 'company' and
            current_user.public_id != data.get('company_id')):
        return jsonify({'Error': 'Invalid access'}), 403

    ignored_fields = ['public_id', 'created_at',
                      'updated_at', 'company_id', 'initial_stock']

    item = storage.get(Items, item_id)
    if not item:
        return jsonify({'Error': 'Item not found'}), 404

    for key, value in data.items():
        if key in ignored_fields:
            return jsonify({"Error": f"{key} cannot be modified"}), 400
        elif key == 'stockamount':
            if not isinstance(value, int) or value < 0:
                return jsonify({"Error": "Invalid stockamount"}), 400
            # Update stockamount and adjust initial_stock
            updated_stock = item.initial_stock + value
            item.stockamount = value
            item.initial_stock = updated_stock
        else:
            setattr(item, key, value)

    try:
        storage.save()
    except IntegrityError as e:
        if 'check_stockamount_non_negative' in str(e.orig):
            return jsonify({'Error':
                            'Stock amount should be non-negative'}), 400
        if 'check_initial_stock_non_negative' in str(e.orig):
            return jsonify({'Error':
                            'Initial stock should be non-negative'}), 400
        if 'check_reorder_level_non_negative' in str(e.orig):
            return jsonify({'Error':
                            'Reorder level should be non-negative'}), 400
        return jsonify({'Error':
                        'Invalid data', 'message': str(e.orig)}), 400

    return jsonify(item.to_dict()), 200


@app_views.route('/items/<item_id>',
                 methods=['DELETE'], strict_slashes=False)
@token_required
def delete_item(current_user, item_id):
    """Delete an item"""
    if current_user.role not in roles:
        jsonify({'Error': 'Invalid access'}), 403

    item = storage.get(Items, item_id)
    if not item:
        return jsonify({'Error': 'Item not found'}), 404

    # restricts companies from accessing other companies' profiles
    if (current_user.role == 'company' and
            current_user.public_id != item.company_id):
        jsonify({'Error': 'Invalid access'}), 403
    try:
        storage.delete(item)
        storage.save()
        return jsonify({"message":
                        f"Item {item.public_id} deleted successfully"}), 200
    except IntegrityError as e:
        return jsonify({"Error during deletion": f"{str(e)}"}), 400
