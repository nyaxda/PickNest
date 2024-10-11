#!/usr/bin/python3
"""Hash Password Module"""

import bcrypt
import hashlib
import base64


def hash_password(password: str) -> str:
    """utility func to hash function"""
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode(), salt)
    return hashed_password.decode()

def verify_password(user_pass, hash):
    """used to verify a user on login"""
    return bcrypt.checkpw(user_pass.encode(), hash.encode())
