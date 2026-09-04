from cryptography.fernet import Fernet
from app.config import settings

_fernet = Fernet(settings.fernet_key.encode())


def encrypt_token(plaintext_token: str) -> str:
    return _fernet.encrypt(plaintext_token.encode()).decode()


def decrypt_token(encrypted_token: str) -> str:
    return _fernet.decrypt(encrypted_token.encode()).decode()