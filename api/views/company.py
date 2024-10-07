#!/usr/bin/python3
"""Company Module"""

from api.views import app_views
from models import storage
from models.company import Company
from flask import jsonify, abort, request, make_response


@app_views.route('/companies',
                 methods=['GET'], strict_slashes=False)
def get_companies():
    """Retrieve list of all companies"""
    all_companies = storage.all(Company).values()
    list_companies = [company.to_dict() for company in all_companies]
    return jsonify(list_companies)


@app_views.route('/companies/<company_id>',
                 methods=['GET'], strict_slashes=False)
def get_company(company_id):
    """Retrieves a company"""
    company = storage.get(Company, company_id)
    if not company:
        abort(400, description="Company not found")
    return jsonify(company.to_dict())


@app_views.route('/companies',
                 methods=['POST'], strict_slashes=False)
def add_company():
    """Creates a company"""
    if not request.get_json():
        abort(400, description="This is not a valid JSON")
    required_fields = ['name', 'email', 'username',
                       'hashed_password', 'phone_number',
                       'address1', 'city', 'state', 'zip', 'country']
    data = request.get_json()
    for field in required_fields:
        if field not in data:
            abort(400, description=f"{field} not found")
    instance = Company(**data)
    instance.save()
    return make_response(jsonify(instance.to_dict()), 201)


@app_views.route('/companies/<company_id>',
                 methods=['PUT'], strict_slashes=False)
def update_company(company_id):
    """Updates a company"""
    if not request.get_json():
        abort(400, description="Not a JSON")
    ignored_fields = ['id', 'created_at', 'updated_at']

    company = storage.get(Company, company_id)
    if not company:
        abort(400, description="Company not found")
    data = request.get_json()
    for key, value in data.items():
        if key not in ignored_fields:
            setattr(company, key, value)
    storage.save()
    return make_response(jsonify(company.to_dict()), 200)


@app_views.route('/companies/<company_id>',
                 methods=['DELETE'], strict_slashes=False)
def delete_company(company_id):
    """Deletes a company"""
    company = storage.get(Company, company_id)
    if not company:
        abort(400, description="No company found")
    storage.delete(company)
    storage.save()

    return(make_response(jsonify({})), 200)
