import hashlib
import hmac
import secrets

def verify_password(plain_password, hashed_password):
    salt, expected = hashed_password.split("$", 1)
    actual = hashlib.pbkdf2_hmac(
        "sha256", plain_password.encode(), salt.encode(), 600_000
    ).hex()
    return hmac.compare_digest(actual, expected)

def get_password_hash(password):
    salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256", password.encode(), salt.encode(), 600_000
    ).hex()
    return f"{salt}${digest}"

