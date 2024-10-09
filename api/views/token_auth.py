#!/usr/bin/env python3
"""wrapper function for token authentication
"""


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
            # obtain user role
            role = decoded_token.get('role')
            roles = ['client', 'company', 'admin']
            if not role and role not in roles:
                jsonify({'Error': 'Invalid role'}), 404

            # get current user in database based on the public_id
            current_user = role.capitalize().query.filter_by(public_id=decoded_token.get('public_id')).first()

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
