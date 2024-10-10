#!/usr/bin/python3
"""Company Module"""

from api.views import app_views
from models import storage
from models.company import Company
from flask import jsonify, abort, request, make_response
from .token_auth import token_required
import bcrypt
import hashlib
import base64
import jwt
from datetime import datetime, timedelta
import json



@app_views.route('companies/sign_up', methods=['POST'], strict_slashes=False)
def company_sign_up() -> json:
    """signing up clients to have accounts"""
    data = request.get_json()

    if not data or not data.get('username') or not data.get('password') or\
            data.get('role'):
        return jsonify({'message': 'Input not Found'}), 404
    
    if data.get('role') != 'company':
        return make_response(jsonify({'message': 'Invalid role'}), 401) 

    hashed = bcrypt.hashpw(
            base64.b64encode(hashlib.sha256(data.get('password')).digest()),
            bcrypt.gensalt()
            )

    company = Company(
            public_id=str(uuid.uuid4()),
            email=data.get('email'),
            hashed_password=hashed,
            full_names=data.get('full_names'),
            phone=data.get('phone'),
            role='company'
            )

    storage.new(company)
    storage.save()

    return jsonify({'message': 'Client registered successfully'}), 201

@app_views.route('companies/login', methods=['POST'], strict_slashes=False)
def company_login():
    """Login route for companies"""
    data = request.get_json()

    if not data or not data.get('username') or not data.get('password') or not data.get('role'):
        return make_response(jsonify({'message': 'Invalid input'}), 400)
    role = data.get('role')
    if role != 'company':
        return make_response(jsonify({'message': 'Invalid role'}), 401)

    company = Company.query.filter_by(username=data['username']).first()

    if not company:
        return jsonify({'message': f'{role.capitalize()} not found!'}), 404

    # Check password match
    if not bcrypt.checkpw(data['password'].encode('utf-8'), company.hashed_password.encode('utf-8')):
        return jsonify({'message': 'Invalid username or uassword'}), 401

    # Generate token
    token = jwt.encode({
        'public_id': company.public_id,
        'role': role,  # Include role in the token for further route protection
        'exp': datetime.utcnow() + timedelta(minutes=10)
        }, app.config['SECRET_KEY'], algorithm='HS256')

    # make response header
    res = make_response(jsonify({'message': f'{role.capitalize()} logged in successfully'}))
    res.headers['access_token'] = token.decode('utf-8') if isinstance(token, bytes) else token
    return res


@token_required
@app_views.route('/companies',
                 methods=['GET'], strict_slashes=False)
def get_companies(current_user):
    """Retrieve list of all companies"""
    if current_user.role != 'admin':
        return jsonify({'message': 'Invalid Access'}), 401

    all_companies = storage.all(Company).values()
    list_companies = [company.to_dict() for company in all_companies]
    return jsonify(list_companies)


@token_required
@app_views.route('/companies/<company_id>',
                 methods=['GET'], strict_slashes=False)
def get_company(current_user, company_id):
    """Retrieves a company"""
    if current_user.role != 'admin':
        return jsonify({'message': 'Invalid Access'}), 401

    company = storage.get(Company, company_id)
    if not company:
        abort(400, description="Company not found")
    return jsonify(company.to_dict())


@token_required
@app_views.route('/companies',
                 methods=['POST'], strict_slashes=False)
def add_company(current_user):
    """Creates a company"""
    if current_user.role != 'admin':
        return jsonify({'message': 'Invalid Access'}), 401

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


@token_required
@app_views.route('/companies/<company_id>',
                 methods=['PUT'], strict_slashes=False)
def update_company(current_user, company_id):
    """Updates a company"""
    if current_user.role != 'admin':
        return jsonify({'message': 'Invalid Access'}), 401

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
def delete_company(current_user, company_id):
    """Deletes a company"""
    roles = ['admin', 'company']
    if current_user.role not in roles:
        return jsonify({'message': 'Invalid Access'}), 401

    company = storage.get(Company, company_id)
    if not company:
        abort(400, description="No company found")

    # check if the a company is deleting it's account associated
    # with its id
    if current_user.role == 'company' and current_user.id != company.id:
        return jsonify({'message': 'Unauthorized action'}), 403

    storage.delete(company)
    storage.save()

    return(make_response(jsonify({})), 200)
