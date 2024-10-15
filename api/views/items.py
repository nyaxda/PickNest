#!/usr/bin/python3
"""Items Module"""

from api.views import app_views
from models import storage
from models.items import Items
from flask import jsonify, abort, request, make_response
from sqlalchemy.exc import IntegrityError
from .token_auth import token_required
from sqlalchemy.exc import IntegrityError



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
    roles = ['admin', 'company']
    if current_user.role not in roles:
        return jsonify({'Error': 'Invalid access'}), 403
    
    item = storage.get(Items, item_id)
    if not item:
        abort(404, description="Item not found")

    # restricts companies from accessing other companies' profiles
    if current_user.role == 'company' and current_user.public_id != item.company_id:
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
        abort(400, description="Not a valid JSON")

    # restricts companies from accessing other companies' profiles
    if current_user.role == 'company' and current_user.public_id != data.get('company_id'):
        return jsonify({'Error': 'Invalid access'}), 403

    required_fields = ['company_id', 'name',
                       'stockamount', 'reorder_level', 'description', 'category', 'SKU']
    for field in required_fields:
        if field not in data:
            abort(400, description=f"{field} is missing")
    # Calculate initial_stock based on stockamount
    data['initial_stock'] = data['stockamount']

    instance = Items(**data)
    try:
        storage.new(instance)
        storage.save()
    except IntegrityError as e:
        if 'Duplicate' in str(e):
            return jsonify({'Error': 'Duplicate SKU'}), 400
        return jsonify({'Error': 'Invalid data', 'message': str(e)}), 400
    return make_response(jsonify({"message": "Item Added Successfully"}), 201)



@app_views.route('/items/<item_id>',
                 methods=['PUT'], strict_slashes=False)
@token_required
def update_item(current_user, item_id):
    """Update an existing item"""
    if current_user.role not in roles:
        return jsonify({'Error': 'Invalid access'}), 403

    data = request.get_json()
    if not data:
        return jsonify({'Error': 'Invalid JSON'}), 400

    # restricts companies from accessing other companies' profiles
    if current_user.role == 'company' and current_user.id != data.get('company_id'):
        return jsonify({'Error': 'Invalid access'}), 403

    ignored_fields = ['id', 'created_at']

    item = storage.get(Items, item_id)
    if not item:
        return jsonify({'message': 'Item not found'}), 404

    if current_user.role == 'company' and current_user.id != item.company_id:
        return jsonify({'Error': 'Invalid access'}), 403


    for key, value in data.items():
        if key not in ignored_fields:
            setattr(item, key, value)
    try: 
        storage.save()
    except IntegrityError as e:
        return jsonify({'Error': 'Invalid data', 'message': str(e)}), 400

    return make_response(jsonify(item.to_dict()), 200)



@app_views.route('/items/<item_id>',
                 methods=['DELETE'], strict_slashes=False)
@token_required
def delete_item(current_user, item_id):
    """Delete an item"""
    if current_user.role not in roles:
        return jsonify({'message': 'Unauthorized action'}), 403

    item = storage.get(Items, item_id)
    if not item:
        return jsonify({'message': 'Item not found'}), 404

    # restricts companies from accessing other companies' profiles
    if current_user.role == 'company' and current_user.id != item.company_id:
        return jsonify({'Error': 'Invalid access'}), 403

    item_name = item.name
    storage.delete(item)
    storage.save()
    return jsonify({'message': f'{item_name} deleted successfully'}), 200


@app_views.route('/items/<item_id>/stock', methods=['PUT'], strict_slashes=False)
@token_required
def update_stock(current_user, item_id):
    """Update the stock amount for an item"""
    if current_user.role not in roles:
        return jsonify({'message': 'Unauthorized action'}), 403

    item = storage.get(Items, item_id)
    if not item:
        return jsonify({'message': 'Item not found'}), 404

    if current_user.role == 'company' and current_user.id != item.company_id:
        return jsonify({'Error': 'Invalid access'}), 403

    data = request.get_json()
    if not data:
        return jsonify({'message': 'Invalid JSON'}), 400

    quantity_ordered = data.get('quantity_ordered')
    quantity_stocked = data.get('quantity_stocked')

    if quantity_ordered and quantity_stocked:
        return jsonify({'message': 'Only one of quantity_ordered or quantity_stocked should be provided'}), 400

    try:
        # If quantity_ordered is provided, decrease stock
        if quantity_ordered is not None:
            if not isinstance(quantity_ordered, int) or quantity_ordered <= 0:
                return jsonify({'message': 'quantity_ordered must be a positive integer'}), 400

            # Perform stock reduction
            item.update_stock(quantity_ordered)

        # If quantity_stocked is provided, increase stock
        if quantity_stocked is not None:
            if not isinstance(quantity_stocked, int) or quantity_stocked <= 0:
                return jsonify({'message': 'quantity_stocked must be a positive integer'}), 400

            # Perform stock addition
            item.restock(quantity_stocked)

        storage.save()
    except ValueError as e:
        return jsonify({'message': str(e)}), 400

    return jsonify({'message': 'Stock updated successfully', 'item': item.to_dict()}), 200


@app_views.route('/items/<item_id>/reorder_check', methods=['GET'], strict_slashes=False)
@token_required
def check_reorder(current_user, item_id):
    """Check if an item is below the reorder level"""
    if current_user.role not in roles:
        return jsonify({'message': 'Unauthorized action'}), 403

    item = storage.get(Items, item_id)
    if not item:
        return jsonify({'message': 'Item not found'}), 404
    if current_user.role == 'company' and current_user.id != item.company_id:
        return jsonify({'Error': 'Invalid access'}), 403

    below_reorder = item.stockamount < item.reorder_level
    message = f"Item {item.name} is {'below' if below_reorder else 'above'} the reorder level"

    return jsonify({'message': message, 'below_reorder_level': below_reorder}), 200
