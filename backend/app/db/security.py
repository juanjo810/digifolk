
from app.core.config import SECRET_KEY, TOKEN_URL, API_PREFIX
from fastapi_login import LoginManager

manager = LoginManager(bytes(str(SECRET_KEY), 'utf-8').hex(), API_PREFIX+TOKEN_URL)

def hash_password(plaintext_password: str):
    """ Return the hash of a password """
    return manager.pwd_context.hash(plaintext_password)

def verify_password(password_input: str, hashed_password: str):
    """ Check if the provided password matches """
    return manager.pwd_context.verify(password_input, hashed_password)
