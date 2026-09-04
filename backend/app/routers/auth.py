import secrets
import httpx
from fastapi import APIRouter, Depends, HTTPException, Response, Request
from fastapi.responses import RedirectResponse
from sqlmodel import Session, select

from app.config import settings
from app.database import get_session
from app.models.user import User
from app.auth.crypto import encrypt_token
from app.auth.session import create_session_token, SESSION_COOKIE_NAME, SESSION_MAX_AGE_SECONDS

router = APIRouter(prefix="/auth/github", tags=["auth"])

GITHUB_AUTHORIZE_URL = "https://github.com/login/oauth/authorize"
GITHUB_TOKEN_URL = "https://github.com/login/oauth/access_token"
GITHUB_USER_API_URL = "https://api.github.com/user"

# Simple in-memory state store for CSRF protection on the OAuth callback.
# Fine for a single-process dev setup. If you ever run multiple backend
# processes/workers, this needs to move to Redis or the DB instead —
# an in-memory set won't be shared across processes.
_pending_states: set[str] = set()


@router.get("/login")
def github_login():
    state = secrets.token_urlsafe(32)
    _pending_states.add(state)

    params = {
        "client_id": settings.github_client_id,
        "redirect_uri": settings.github_oauth_callback_url,
        "scope": "read:user",  # public profile data only — no repo write access needed
        "state": state,
    }
    query = "&".join(f"{k}={v}" for k, v in params.items())
    return RedirectResponse(f"{GITHUB_AUTHORIZE_URL}?{query}")


@router.get("/callback")
async def github_callback(
    code: str,
    state: str,
    session: Session = Depends(get_session),
):
    if state not in _pending_states:
        raise HTTPException(status_code=400, detail="Invalid or expired OAuth state")
    _pending_states.discard(state)

    async with httpx.AsyncClient() as client:
        # Exchange the temporary code for an access token
        token_resp = await client.post(
            GITHUB_TOKEN_URL,
            data={
                "client_id": settings.github_client_id,
                "client_secret": settings.github_client_secret,
                "code": code,
                "redirect_uri": settings.github_oauth_callback_url,
            },
            headers={"Accept": "application/json"},
        )
        token_data = token_resp.json()
        access_token = token_data.get("access_token")

        if not access_token:
            raise HTTPException(status_code=400, detail="GitHub token exchange failed")

        # Fetch the user's public GitHub profile using that token
        user_resp = await client.get(
            GITHUB_USER_API_URL,
            headers={
                "Authorization": f"Bearer {access_token}",
                "Accept": "application/vnd.github+json",
            },
        )
        gh_user = user_resp.json()

    github_id = gh_user["id"]
    github_username = gh_user["login"]

    # Upsert: does this GitHub user already have a DevCard account?
    existing = session.exec(select(User).where(User.github_id == github_id)).first()

    encrypted = encrypt_token(access_token)

    if existing:
        existing.github_username = github_username
        existing.display_name = gh_user.get("name")
        existing.avatar_url = gh_user.get("avatar_url")
        existing.encrypted_github_token = encrypted
        session.add(existing)
        session.commit()
        session.refresh(existing)
        user = existing
    else:
        user = User(
            github_id=github_id,
            github_username=github_username,
            display_name=gh_user.get("name"),
            avatar_url=gh_user.get("avatar_url"),
            encrypted_github_token=encrypted,
        )
        session.add(user)
        session.commit()
        session.refresh(user)

    session_token = create_session_token(user.id)

    response = RedirectResponse(url=settings.frontend_url)
    response.set_cookie(
        key=SESSION_COOKIE_NAME,
        value=session_token,
        max_age=SESSION_MAX_AGE_SECONDS,
        httponly=True,       # JS on the frontend can never read this cookie
        secure=False,        # MUST be True in production (HTTPS only)
        samesite="lax",
    )
    return response


@router.get("/logout")
def logout(response: Response):
    response.delete_cookie(SESSION_COOKIE_NAME)
    return {"message": "Logged out"}