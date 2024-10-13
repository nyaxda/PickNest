#!/usr/bin/env python3
"""Wrapper function for token authentication"""
from functools import wraps
from flask import request, jsonify, make_response, current_app as app
import jwt
from models.client import Client
from models.company import Company
from models import storage


def token_required(fn):
    """wrapper fn to secure routes
    Args:
        fn: function being wrapped
    Returns:
        wrapped function with appended user details or
        error upon token absence, invalidity or expiry
    """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        token = request.headers.get('access-token')
        if not token:
            return make_response(
                jsonify({'Error': 'No Token Found'}),
                401,
                {'WWW-Authenticate': 'Basic realm="Login required!"'}
            )

        try:
            # Decode token
            decoded_token = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            # Obtain user role
            role = decoded_token.get('role')
            roles = ['client', 'company', 'admin']
            if not role or role not in roles:
                return jsonify({'Error': 'Invalid role'}), 403

            # Get current user in the database based on the public_id
            if role == 'client':
                current_user = storage.get(Client, decoded_token.get('public_id'))
            elif role == 'company':
                current_user = storage.get(Company, decoded_token.get('public_id'))

            if not current_user:  # Token is valid but user doesn't exist
                return jsonify({'Error': 'User not found'}), 404

        except jwt.ExpiredSignatureError:
            return jsonify({'Message': 'Token Expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'Message': 'Invalid Token'}), 401
        except jwt.DecodeError:
            return jsonify({'Message': 'Error Decoding Token'}), 401

        # If everything is fine, pass current_user to the wrapped function
        return fn(current_user, *args, **kwargs)
    return wrapper
