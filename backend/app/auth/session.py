from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
from app.config import settings

SESSION_COOKIE_NAME = "devcard_session"
SESSION_MAX_AGE_SECONDS = 60 * 60 * 24 * 14  # 14 days

_serializer = URLSafeTimedSerializer(settings.secret_key, salt="devcard-session")


def create_session_token(user_id: int) -> str:
    """Produces a signed, tamper-proof string encoding the user_id.
    Safe to put directly in a cookie value.
    """
    return _serializer.dumps({"user_id": user_id})


def verify_session_token(token: str) -> int | None:
    """Returns the user_id if the token is valid and not expired/tampered.
    Returns None if invalid — caller should treat as 'not logged in',
    never raise this as an error to the client.
    """
    try:
        data = _serializer.loads(token, max_age=SESSION_MAX_AGE_SECONDS)
        return data["user_id"]
    except (BadSignature, SignatureExpired, KeyError):
        return None