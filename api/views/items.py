#!/usr/bin/python3
"""Items Module"""

from api.views import app_views
from models import storage
from models.items import Items
from flask import jsonify, abort, request, make_response
from .token_auth import token_required


@token_required
@app_views.route('/companies/<company_id>/items',
                 methods=['GET'], strict_slashes=False)
def get_company_items(current_user, company_id):
    """Retrieve all items from a specific company"""
    roles = ['admin', 'company']
    if current_user.role not in roles:
        jsonify({'Error': 'Invalid access'}), 403
    
    # restricts companies from accessing other companies' profiles
    if current_user.role == 'company' and current_user.id != company_id:
        jsonify({'Error': 'Invalid access'}), 403

    all_items = storage.all(Items).values()
    list_items = [item.to_dict() for
                  item in all_items if item.company_id == company_id]
    return jsonify(list_items)


@token_required
@app_views.route('/items/<item_id>',
                 methods=['GET'], strict_slashes=False)
def get_item(current_user, item_id):
    """Retrieve a specific item"""
    roles = ['admin', 'company']
    if current_user.role not in roles:
        jsonify({'Error': 'Invalid access'}), 403
    
    item = storage.get(Items, item_id)
    if not item:
        abort(404, description="Item not found")

    # restricts companies from accessing other companies' profiles
    if current_user.role == 'company' and current_user.id != item.company_id:
        jsonify({'Error': 'Invalid access'}), 403
    return jsonify(item.to_dict())


@token_required
@app_views.route('/items',
                 methods=['POST'], strict_slashes=False)
def add_item(current_id):
    """Create a new item"""
    roles = ['admin', 'company']
    if current_user.role not in roles:
        jsonify({'Error': 'Invalid access'}), 403

    data = request.get_json()
    if not data:
        abort(400, description="Not a valid JSON")

    # restricts companies from accessing other companies' profiles
    if current_user.role == 'company' and current_user.id != data.get('company_id'):
        jsonify({'Error': 'Invalid access'}), 403

    required_fields = ['company_id', 'name',
                       'stockamount', 'description', 'category', 'SKU']
    for field in required_fields:
        if field not in data:
            abort(400, description=f"{field} is missing")
    instance = Items(**data)
    instance.save()
    return make_response(jsonify(instance.to_dict()), 201)


@token_required
@app_views.route('/items/<item_id>',
                 methods=['PUT'], strict_slashes=False)
def update_item(current_item, item_id):
    """Update an existing item"""
    roles = ['admin', 'company']
    if current_user.role not in roles:
        jsonify({'Error': 'Invalid access'}), 403

    data = request.get_json()
    if not data:
        abort(400, description="Not a valid JSON")

    # restricts companies from accessing other companies' profiles
    if current_user.role == 'company' and current_user.id != data.get('company_id'):
        jsonify({'Error': 'Invalid access'}), 403

    ignored_fields = ['id', 'created_at', 'updated_at']

    item = storage.get(Items, item_id)
    if not item:
        abort(404, description="Item not found")

    for key, value in data.items():
        if key not in ignored_fields:
            setattr(item, key, value)
    storage.save()
    return make_response(jsonify(item.to_dict()), 200)


@token_required
@app_views.route('/items/<item_id>',
                 methods=['DELETE'], strict_slashes=False)
def delete_item(current_id, item_id):
    """Delete an item"""
    roles = ['admin', 'company']
    if current_user.role not in roles:
        jsonify({'Error': 'Invalid access'}), 403

    item = storage.get(Items, item_id)
    if not item:
        abort(404, description="Item not found")

    # restricts companies from accessing other companies' profiles
    if current_user.role == 'company' and current_user.id != item.company_id:
        jsonify({'Error': 'Invalid access'}), 403

    storage.delete(item)
    storage.save()
    return make_response(jsonify({}), 200)
