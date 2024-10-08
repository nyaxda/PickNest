from api.views import app_views
import jwt
from flask import jsonify, make_response, request
from datetime import datetime, timedelta
import bcrypt
import uuid
import hashlib
import base64
from functools import wraps
from .api.views import app_views
import .models import storage
from models.client import Client
from models.company import Company

app = Flask(__name__)
app.register_blueprint(app_views)

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
            # decode token
            decoded_token = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            # get current user in database based on the public_id
            current_user = Client.query.filter_by(public_id=decoded_token.get('public_id')).first()

            if not current_user:  # token is valid but user doesn't exist
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


@app.route('/sign_up', methods=['POST'], strict_slashes=False)
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
        return jsonify({'message': 'Invalid Username or Password!'}), 401
    
    # password match check
    if not bcrypt.checkpw(data['password'].encode('utf-8'),
            client.hashed_password.encode('utf-8')):
        return jsonify({'message': 'Invalid Username or Password'}), 401
    
    # generate token
    token = jwt.encode({
        'public_id': client.public_id,
        'exp': datetime.utcnow() + timedelta(minutes=10)
        }, app.config['SECRET_KEY'], algorithm='HS256')
    
    res = make_response(jsonify({'message': 'Login successful'}), 200)
    res.headers['access-token'] = token.decode('utf-8') if isinstance(token, bytes) else token
    return res
