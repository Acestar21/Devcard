import json
from fastapi import APIRouter, Depends, HTTPException, Response
from sqlmodel import Session, select

from app.database import get_session
from app.models.user import User
from app.models.github_stats import GithubStatsCache

router = APIRouter(prefix="/badge", tags=["badges"])

def generate_badge_svg(username: str, stats: GithubStatsCache | None) -> str:
    if not stats:
        return f'''<svg width="300" height="100" xmlns="http://www.w3.org/2000/svg">
            <rect width="100%" height="100%" rx="10" fill="#f3f4f6" />
            <text x="50%" y="50%" dominant-baseline="middle" text-anchor="middle" fill="#6b7280" font-family="sans-serif" font-size="14">
                Stats not yet available for {username}
            </text>
        </svg>'''

    languages = json.loads(stats.top_languages_json)
    lang_text = ", ".join(languages[:3]) if languages else "None"
    if len(languages) > 3:
        lang_text += f" +{len(languages) - 3}"

    return f'''<svg width="300" height="100" xmlns="http://www.w3.org/2000/svg">
        <rect width="100%" height="100%" rx="10" fill="#1a1b27" />
        <text x="20" y="30" fill="#ffffff" font-family="sans-serif" font-size="16" font-weight="bold">@{username}</text>
        <text x="20" y="60" fill="#9ca3af" font-family="sans-serif" font-size="12">Contributions: {stats.total_contributions}</text>
        <text x="20" y="80" fill="#9ca3af" font-family="sans-serif" font-size="12">Top: {lang_text}</text>
    </svg>'''

@router.get("/{username}")
def get_badge(
    username: str,
    db: Session = Depends(get_session),
):
    user = db.exec(select(User).where(User.github_username == username)).first()
    if not user:
        svg_content = f'''<svg width="300" height="100" xmlns="http://www.w3.org/2000/svg">
            <rect width="100%" height="100%" rx="10" fill="#f3f4f6" />
            <text x="50%" y="50%" dominant-baseline="middle" text-anchor="middle" fill="#6b7280" font-family="sans-serif" font-size="14">
                User "{username}" not found
            </text>
        </svg>'''
        return Response(content=svg_content, media_type="image/svg+xml", status_code=404)

    cache = db.exec(
        select(GithubStatsCache).where(GithubStatsCache.user_id == user.id)
    ).first()

    svg_content = generate_badge_svg(username, cache)

    return Response(
        content=svg_content,
        media_type="image/svg+xml",
        headers={"Cache-Control": "public, max-age=3600"}
    )