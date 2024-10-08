#!/usr/bin/python3
"""Client Module"""

from api.views import app_views
from models import storage
from models.client import Client
from flask import jsonify, abort, request, make_response


@app.route('clients/sign_up', methods=['POST'], strict_slashes=False)
def sign_up() -> json:
    """signing up clients to have accounts"""
    data = request.get_json()

    if not data or not data.get('username') or not data.get('password') or\
            data.get('role'):
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
            role='client'
            )

    storage.new(client)
    storage.save()

    return jsonify({'message': 'Client registered successfully'}), 201


@app_views.route('clients/login', methods=['POST'], strict_slashes=False)
def login():
    """Login route for both clients and companies"""
    data = request.get_json()

    if not data or not data.get('username') or not data.get('password') or not data.get('role'):
        return make_response(jsonify({'message': 'Invalid input'}), 400)

    if data.get('role') != 'client':
        return make_response(jsonify({'message': 'Invalid role'}), 401)

    user = Client.query.filter_by(username=data['username']).first()

    if not user:
        return jsonify({'message': f'{role.capitalize()} not found!'}), 404

    # Check password match
    if not bcrypt.checkpw(data['password'].encode('utf-8'), user.hashed_password.encode('utf-8')):
        return jsonify({'message': 'Incorrect Password'}), 401

    # Generate token
    token = jwt.encode({
        'public_id': user.public_id,
        'role': role,  # Include role in the token for further route protection
        'exp': datetime.utcnow() + timedelta(minutes=10)
        }, app.config['SECRET_KEY'], algorithm='HS256')

    # make response header
    res = make_response(jsonify({'message': f'{role.capitalize()} logged in successfully',)})
    res.headers['access_token'] = token.decode('utf-8') if isinstance(token, bytes) else token
    return res


@token_required
@app_views.route('/clients',
                 methods=['GET'], strict_slashes=False)
def get_clients(current_user):
    """Retrieve list of all clients"""
    if current_user.role != 'admin':
        return jsonify({'message': 'Unauthorized action'}), 403
    all_clients = storage.all(Client).values()
    list_clients = [client.to_dict() for client in all_clients]
    return jsonify(list_clients)


@app_views.route('/clients/<client_id>',
                 methods=['GET'], strict_slashes=False)
def get_client(current_user, client_id):
    """Retrieves a client"""
    if current_user.role != 'admin':
        return jsonify({'message': 'Invalid access'})

    client = storage.get(Client, client_id)
    if not client:
        abort(404)
    return jsonify(client.to_dict())


@token_authorized
@app_views.route('/clients',
                 methods=['POST'], strict_slashes=False)
def add_client(current_user):
    """Creates a client"""
    if current_user.role != 'admin':
        return jsonify({'message': 'Invalid access'})

    if not request.get_json():
        abort(400, description="This is not a valid JSON")
    required_fields = ['firstname', 'middlename', 'lastname',
                       'username', 'hashed_password',
                       'email', 'phone']
    data = request.get_json()
    for field in required_fields:
        if field not in data:
            abort(400, description=f"{field} not found")
    instance = Client(**data)
    instance.save()
    return make_response(jsonify(instance.to_dict()), 201)


@token_authorized
@app_views.route('/clients/<client_id>',
                 methods=['PUT'], strict_slashes=False)
def update_client(client_id):
    """Updates a client"""
    if not request.get_json():
        abort(404, description="Not a valid JSON")
    ignored_fields = ['id', 'created_at', 'updated_at']

    client = storage.get(Client, client_id)
    if not client:
        abort(400, description="Client not found")
    data = request.get_json()
    for key, value in data.items():
        if key not in ignored_fields:
            setattr(client, key, value)
    storage.save()
    return make_response(jsonify(client.to_dict()), 200)


@token_required
@app_views.route('/clients/<client_id>',
                 methods=['DELETE'], strict_slashes=False)
def delete_client(current_user, client_id):
    """Deletes a client"""
    roles = ['admin', 'client']
    if current_user.role not in roles:
        return jsonify({'message': 'Invalid access'}), 401

    client = storage.get(Client, client_id)
    if not client:
        abort(404, description="No client found")

    if current_user.role is 'client' and current_user.id != client.id:
        return jsonify({'message': 'Unauthorized action'}), 403 

    storage.delete(client)
    storage.save()

    return(make_response(jsonify({})), 200)
