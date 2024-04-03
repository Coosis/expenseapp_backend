from flask import Flask, request, jsonify
import json
import jwt
import datetime
from functools import wraps

def create_token(user_id, username):
    payload = {
        'user_id': user_id,
        'user_name': username,
        # 'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1)
        'exp' : datetime.datetime.utcnow() + datetime.timedelta(seconds=20)
    }
    token = jwt.encode(payload, 'secret', algorithm='HS256')
    return token

def token_required(f):
    """
    handles the token extraction and verification.
    use @token_required to specify that a route requires a token.
    payload is passed to the function if the token is valid.
    """

    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
            
        # Check if the token is in the Authorization header and extract it
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            token = auth_header.split(" ")[1] if len(auth_header.split(" ")) > 1 else None
        
        if not token:
            return jsonify({'message': 'Token is missing!'}), 403

        try:
            # Decode the token using PyJWT
            payload = jwt.decode(token, 'secret', algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired!'}), 401  # 401 for Unauthorized
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Invalid token!'}), 401
        
        # Proceed with the original function, you can pass user_id or other data if needed
        return f(payload, *args, **kwargs)
    
    return decorated