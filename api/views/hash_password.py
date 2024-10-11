import bcrypt
import hashlib
import base64


def hash_password(password: str) -> str:
    """utility func to hash function"""
    return bcrypt.hashpw(
        base64.b64encode(hashlib.sha256(password.encode('utf-8')).digest()),
        bcrypt.gensalt()
    ).decode('utf-8')
