#!/usr/bin/python3
"""Company Module"""

from api.views import app_views
from models import storage
from models.company import Company
from flask import jsonify, abort, request, make_response, current_app
from sqlalchemy.exc import IntegrityError
from .token_auth import token_required
from datetime import datetime, timedelta
import jwt
import uuid
from .hash_password import hash_password, verify_password

roles = ['admin', 'company']


@app_views.route('/companies/sign_up', methods=['POST'], strict_slashes=False)
def company_sign_up():
    """Sign-up companies to have accounts"""
    data = request.get_json()

    # Check for required fields in the request
    required_fields = ['name', 'username', 'password', 'email', 'phone_number', 'address1', 'city', 'state', 'zip', 'country']
    for field in required_fields:
        if field not in data:
            return jsonify({'message': f'{field} is required'}), 400

    # Hash the password
    hashed_password = hash_password(data.get('password'))

    # Create a new company instance
    company = Company(
        public_id=str(uuid.uuid4()),
        name=data.get('name'),
        username=data.get('username'),
        hashed_password=hashed_password,
        email=data.get('email'),
        phone_number=data.get('phone_number'),
        address1=data.get('address1'),
        address2=data.get('address2', ''),  # Optional field
        city=data.get('city'),
        state=data.get('state'),
        zip=data.get('zip'),
        country=data.get('country'),
        role='company'
    )

    try:
        # Save the new company to storage
        storage.new(company)
        storage.save()

    except IntegrityError as e:
        storage.rollback()  # Rollback session in case of an error

        # Handle unique constraint violations for username, email, or phone_number
        if "username" in str(e.orig):
            return jsonify({'message': 'Username already exists'}), 409
        elif "email" in str(e.orig):
            return jsonify({'message': 'Email already exists'}), 409
        elif "phone_number" in str(e.orig):
            return jsonify({'message': 'Phone number already exists'}), 409
        else:
            return jsonify({'message': 'An error occurred during registration'}), 500

    return jsonify({'message': 'Company registered successfully'}), 201


@app_views.route('/companies/login', methods=['POST'], strict_slashes=False)
def company_login():
    """Login route for companies"""
    data = request.get_json()

    if not data or not data.get('username') or not data.get('password') or not data.get('role'):
        return make_response(jsonify({'message': 'Invalid input'}), 400)

    if data.get('role') != 'company':
        return make_response(jsonify({'message': 'Invalid role'}), 401)

    # Query the company by username
    all_companies = storage.all(Company)
    company = next((comp for comp in all_companies if comp.username == data.get('username')), None)
    if not company:
        return jsonify({'message': 'Company not found!'}), 404

    # Check if the password matches
    if not verify_password(data.get('password'), company.hashed_password):
        return jsonify({'message': 'Incorrect Password'}), 401

    # Generate token
    token = jwt.encode({
        'public_id': company.public_id,
        'role': 'company',
        'exp': datetime.utcnow() + timedelta(minutes=120)
    }, current_app.config['SECRET_KEY'], algorithm='HS256')

    return jsonify({'message': 'Company logged in successfully',
        'token': token if isinstance(token, str) else token.decode('utf-8')})


@app_views.route('/companies', methods=['GET'], strict_slashes=False)
@token_required
def get_companies(current_user):
    """Retrieve list of all companies"""
    if current_user.role != 'admin':
        return jsonify({'message': 'Unauthorized access'}), 403

    all_companies = storage.all(Company)
    list_companies = [company.to_dict() for company in all_companies]
    return jsonify(list_companies)


@app_views.route('/companies/<company_id>', methods=['GET'], strict_slashes=False)
@token_required
def get_company(current_user, company_id):
    """Retrieve a company by ID"""
    if current_user.role not in roles:
        return jsonify({'message': 'Unauthorized access'}), 403

    company = storage.get(Company, company_id)
    if not company:
        return jsonify({'message': 'Company not found'}), 404

    if current_user.role == 'company' and current_user.public_id != company.public_id:
        return jsonify({'message': 'Unauthorized access'}), 403

    return jsonify(company.to_dict())


@app_views.route('/companies', methods=['POST'], strict_slashes=False)
@token_required
def add_company(current_user):
    """Create a new company"""
    if current_user.role != 'admin':
        return jsonify({'message': 'Unauthorized action'}), 403

    if not request.get_json():
        abort(400, description="Not a valid JSON")

    required_fields = ['name', 'email', 'username', 'hashed_password', 'phone_number', 'address1', 'city', 'state', 'zip', 'country']
    data = request.get_json()

    for field in required_fields:
        if field not in data:
            abort(400, description=f"{field} not found")

    instance = Company(**data)
    storage.new(instance)
    storage.save()

    return make_response(jsonify(instance.to_dict()), 201)


@app_views.route('/companies/<company_id>', methods=['PUT'], strict_slashes=False)
@token_required
def update_company(current_user, company_id):
    """Updates a company"""
    if current_user.role not in roles:
        return jsonify({'message': 'Unauthorized access'}), 403

    data = request.get_json()
    if not data:
        return jsonify({'message': 'Not a valid JSON'}), 400

    ignored_fields = ['id', 'created_at']

    # Fetch the company from storage
    company = storage.get(Company, company_id)
    if not company:
        return jsonify({'message': 'Company not found'}), 404

    # Restrict access to only the company's own account if they are a company
    if current_user.role == 'company' and current_user.public_id != company.public_id:
        return jsonify({'message': 'Unauthorized access'}), 403

    for key, value in data.items():
        if key not in ignored_fields:
            if key == 'password':
                # Hash the updated password
                value = hash_password(value)
                setattr(company, 'hashed_password', value)
            else:
                setattr(company, key, value)

    # Update the updated_at timestamp
    setattr(company, 'updated_at', datetime.utcnow())

    # Save changes to storage
    storage.save()

    return jsonify(company.to_dict()), 200


@app_views.route('/companies/<company_id>', methods=['DELETE'], strict_slashes=False)
@token_required
def delete_company(current_user, company_id):
    """Delete a company by ID"""
    if current_user.role not in roles:
        return jsonify({'message': 'Unauthorized action'}), 401

    company = storage.get(Company, company_id)
    if not company:
        abort(404, description="Company not found")

    if current_user.role == 'company' and current_user.public_id != company.public_id:
        return jsonify({'message': 'Unauthorized action'}), 403

    storage.delete(company)
    storage.save()

    return jsonify({'message': f'{company.name} removed'}), 200

