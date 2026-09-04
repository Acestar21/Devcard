import json
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.database import get_session
from app.models.user import User
from app.models.github_stats import GithubStatsCache
from app.auth.dependencies import get_current_user_optional
from app.services.github import is_stale, fetch_and_cache_stats, GithubTokenInvalid


router = APIRouter(prefix="/profiles", tags=["profiles"])

@router.get("/{username}")
async def get_profile(
    username: str,
    db: Session = Depends(get_session),
    viewer: User | None = Depends(get_current_user_optional),
):
    user = db.exec(select(User).where(User.github_username == username)).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    cache = db.exec(
        select(GithubStatsCache).where(GithubStatsCache.user_id == user.id)
    ).first()

    if is_stale(cache):
        try:
            cache = await fetch_and_cache_stats(user, db)
        except GithubTokenInvalid as e:
            print(f"DEBUG: stats fetch failed: {e}")

    if not cache:
        raise HTTPException(status_code=404, detail="GitHub stats currently unavailable and no cached data exists")

    is_owner = False
    if viewer and viewer.id == user.id:
        is_owner = True


    return {
        "username": user.github_username,
        "display_name": user.display_name,
        "avatar_url": user.avatar_url,
        "bio": user.bio,
        "stats": {
            "total_contributions": cache.total_contributions,
            "top_languages": json.loads(cache.top_languages_json),
            "pinned_repos": json.loads(cache.pinned_repos_json),
        },
        "is_owner": is_owner,
    }