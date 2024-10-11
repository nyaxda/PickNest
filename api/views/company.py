#!/usr/bin/python3
"""Company Module"""

from api.views import app_views
from models import storage
from models.company import Company
from flask import jsonify, abort, request, make_response
from sqlalchemy.exc import IntegrityError
from .token_auth import token_required
import jwt
from datetime import datetime, timedelta
import json
import uuid
from .hash_password import hash_password

roles = ['admin', 'company']


@app_views.route('companies/sign_up', methods=['POST'], strict_slashes=False)
def company_sign_up() -> json:
    """signing up clients to have accounts"""
    data = request.get_json()

    if not data or not data.get('username') or not data.get('password'):
        return jsonify({'message': 'Input not Found'}), 404
    
    if not data.get('role') or data.get('role') != 'company':
        return make_response(jsonify({'message': 'Invalid role'}), 401)

    required_fields = ['name', 'username', 'password',
                       'email', 'phone_number',
                       'address1', 'address2', 'city',
                       'state', 'zip', 'country'
                      ]

    for field in required_fields:
        if field not in data:
            return jsonify({'message': f"{field} not found"}), 400

    hashed = hash_password(data.get('password'))

    company = Company(
            public_id=str(uuid.uuid4()),
            name=data.get('name'),
            username=data.get('username'),
            hashed_password=hashed,
            email=data.get('email'),
            address1=data.get('address1'),
            address2=data.get('address2'),
            phone_number=data.get('phone_number'),
            city=data.get('city'),
            state=data.get('state'),
            zip=data.get('zip'),
            country=data.get('country'),
            role='company'
            )
    # Try saving to the database and handle IntegrityError if any unique field is violated
    try:
        storage.new(company)
        storage.save()
    except IntegrityError:
        storage.rollback()  # Rollback in case of failure
        return jsonify({'message': 'A company with that username, email, or phone number already exists.'}), 409

    return jsonify({'message': 'Client registered successfully'}), 201

@app_views.route('companies/login', methods=['POST'], strict_slashes=False)
def company_login():
    """Login route for companies"""
    data = request.get_json()

    if not data or not data.get('username') or not data.get('password'):
        return make_response(jsonify({'message': 'Invalid credentials'}), 400)
    role = data.get('role')
    if role != 'company':
        return make_response(jsonify({'message': 'Invalid role'}), 401)

    company = Company.query.filter_by(username=data['username']).first()

    if not company:
        return jsonify({'message': f'{role.capitalize()} not found!'}), 404

    # Check password match
    if not bcrypt.checkpw(data['password'].encode('utf-8'), company.hashed_password.encode('utf-8')):
        return jsonify({'message': 'Invalid credentials'}), 401

    # Generate token
    token = jwt.encode({
        'public_id': company.public_id,
        'role': role,  # Include role in the token for further route protection
        'exp': datetime.utcnow() + timedelta(minutes=120)
        }, app.config['SECRET_KEY'], algorithm='HS256')

    # make response header
    res = make_response(jsonify({
        'message': f'{role.capitalize()} logged in successfully',
        'token': token.decode('utf-8') if isinstance(token, bytes) else token
    }))
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
    if current_user.role not in roles:
        return jsonify({'message': 'Invalid Access'}), 401

    company = storage.get(Company, company_id)
    if not company:
        return jsonify({'message': 'company not found'}), 400

    if current_user.role == 'company' and current_user.public_id != company.public_id:
        return jsonify({'message': 'Unauthorized action'}), 403

    return jsonify(company.to_dict())


@token_required
@app_views.route('/companies',
                 methods=['POST'], strict_slashes=False)
def add_company(current_user):
    """Creates a company"""
    if current_user.role != 'admin':
        return jsonify({'message': 'Invalid Access'}), 403

    if not request.get_json():
        return jsonify({'message': 'Invalid Access'}), 400
    required_fields = ['name', 'email', 'username',
                       'password', 'phone_number',
                       'address1', 'city', 'state', 'zip', 'country']
    data = request.get_json()
    for field in required_fields:
        if field not in data:
            return jsonify({'message': f"{field} not found"}), 400
    
    data['hashed_password'] = hash_password(data.get('password'))
    del data['password']   # delete to prevent collision in field during obj instantiation

    instance = Company(**data)
    instance.save()
    return jsonify(instance.to_dict()), 201


@token_required
@app_views.route('/companies/<company_id>',
                 methods=['PUT'], strict_slashes=False)
def update_company(current_user, company_id):
    """Updates a company"""
    if current_user.role not in roles:
        return jsonify({'message': 'Invalid Access'}), 401

    if not request.get_json():
        return jsonify({'message': 'Invalid JSON'}), 400
    ignored_fields = ['id', 'created_at']

    company = storage.get(Company, company_id)
    if not company:
        return jsonify({'message': 'Company not found'}), 400

    data = request.get_json()

    for key, value in data.items():
        if key not in ignored_fields:
            if key == 'password':  # hash the password
                value = bcrypt.hashpw(
                    base64.b64encode(hashlib.sha256(value).digest()),
                    bcrypt.gensalt())
                setattr(company, 'hashed_password', value)
                continue

            setattr(company, key, value)
    setattr(company, 'updated_at', datetime.utcnow())  # update modification timestamp
    storage.save()
    return jsonify(company.to_dict()), 200


@app_views.route('/companies/<company_id>',
                 methods=['DELETE'], strict_slashes=False)
def delete_company(current_user, company_id):
    """Deletes a company"""
    if current_user.role not in roles:
        return jsonify({'message': 'Invalid Access'}), 401

    company = storage.get(Company, company_id)
    if not company:
        return jsonify({'message': 'Company not found'}), 400

    # check if the a company is deleting it's account associated
    # with its id
    if current_user.role == 'company' and current_user.public_id != company.public_id:
        return jsonify({'message': 'Unauthorized action'}), 403

    storage.delete(company)
    storage.save()

    return(make_response(jsonify({})), 200)
