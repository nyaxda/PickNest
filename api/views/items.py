#!/usr/bin/python3
"""Items Module"""

from api.views import app_views
from models import storage
from models.items import Items
from flask import jsonify, abort, request, make_response


@app_views.route('/companies/<company_id>/items',
                 methods=['GET'], strict_slashes=False)
def get_company_items(company_id):
    """Retrieve all items from a specific company"""
    all_items = storage.all(Items).values()
    list_items = [item.to_dict() for
                  item in all_items if item.company_id == company_id]
    return jsonify(list_items)


@app_views.route('/items/<item_id>',
                 methods=['GET'], strict_slashes=False)
def get_item(item_id):
    """Retrieve a specific item"""
    item = storage.get(Items, item_id)
    if not item:
        abort(404, description="Item not found")
    return jsonify(item.to_dict())


@app_views.route('/items',
                 methods=['POST'], strict_slashes=False)
def add_item():
    """Create a new item"""
    if not request.get_json():
        abort(400, description="Not a valid JSON")
    required_fields = ['company_id', 'name',
                       'stockamount', 'description', 'category', 'SKU']
    data = request.get_json()
    for field in required_fields:
        if field not in data:
            abort(400, description=f"{field} is missing")
    instance = Items(**data)
    instance.save()
    return make_response(jsonify(instance.to_dict()), 201)


@app_views.route('/items/<item_id>',
                 methods=['PUT'], strict_slashes=False)
def update_item(item_id):
    """Update an existing item"""
    if not request.get_json():
        abort(400, description="Not a valid JSON")
    ignored_fields = ['id', 'created_at', 'updated_at']

    item = storage.get(Items, item_id)
    if not item:
        abort(404, description="Item not found")
    data = request.get_json()
    for key, value in data.items():
        if key not in ignored_fields:
            setattr(item, key, value)
    storage.save()
    return make_response(jsonify(item.to_dict()), 200)


@app_views.route('/items/<item_id>',
                 methods=['DELETE'], strict_slashes=False)
def delete_item(item_id):
    """Delete an item"""
    item = storage.get(Items, item_id)
    if not item:
        abort(404, description="Item not found")
    storage.delete(item)
    storage.save()
    return make_response(jsonify({}), 200)
