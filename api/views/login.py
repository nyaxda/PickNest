from api.views import app_views
import jwt
from flask import jsonify, make_response, request
from datetime import datetime, timedelta
import bcrypt
import uuid
import hashlib
import base64
from models.client import Client
from run import session

@app_views.route('/sign_up', methods=['POST'], strict_slashes=False)
def sign_up() -> json:
    """signing up clients to have accounts"""
    data = request.get_json()

    if not data or not data.get('username') or not data.get('password'):
        return jsonify({'message': 'Input not Found'}), 404

    hashed = bcrypt.hashpw(
            base64.b64encode(hashlib.sha256(data.get('password')).digest()),
            bcrypt.gensalt()
            )

    client = Client(
            public_id=str(uuid.uuid4()),
            email=data.get('email'),
            hashed_password=hashed,
            full_names=data.get('full_names'),
            phone=data.get('phone'),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
            )

    session.add(client)
    session.commit()
    return jsonify({'message': 'Client registered successfully'}), 201

@app_views.route('/login', strict_slashes=False)
def login() -> json:
    """implements login feature
    Returns:
        a json message indicating successful token response
        or error
    """
    data = request.get_json()

    # check if user data in form is valid
    if not data or not data.get('username') or not data.get('password'):
        return make_response(jsonify({
            'message': 'Could not verify'}),
            400,
            {'WWW-Authenticate' : 'Basic realm="Login required!"'}
            )
    
    # check user existence
    client = Client.query.filter_by(username=data['username']).first()
    if not client:
        return jsonify('Client Not Found!'), 404
    
    # password match check
    if not bcrypt.checkpw(data['password'].encode('utf-8'),
            client.hashed_password.encode('utf-8')):
        return jsonify({'message': 'Incorrect Password'}), 401
    
    # generate token
    token = jwt.encode({
        'public_id': client.public_id,
        'exp': datetime.utcnow() + timedelta(minutes=10)
        }, app.config['SECRET_KEY'])
    
    res = make_response(jsonify({'message': 'Login successful'}), 200)
    res.headers['token'] = token.decode('utf-8') if isinstance(token, bytes) else token
    return res
