import httpx
from datetime import datetime
from sqlmodel import Session, select

from app.models.user import User
from app.models.github_stats import GithubStatsCache
from app.auth.crypto import decrypt_token

GITHUB_GRAPHQL_URL = "https://api.github.com/graphql"

STALE_AFTER_HOURS = 6

# Minimal GraphQL query for Phase 1: total contributions + top languages
# from the user's most recently pushed repos. Kept simple on purpose —
# pinned repos / more detail can be added later without breaking this shape.
STATS_QUERY = """
query($login: String!) {
  user(login: $login) {
    contributionsCollection {
      contributionCalendar {
        totalContributions
      }
    }
    repositories(first: 10, orderBy: {field: PUSHED_AT, direction: DESC}, ownerAffiliations: OWNER) {
      nodes {
        name
        stargazerCount
        url
        description
        primaryLanguage {
          name
        }
      }
    }
  }
}
"""


class GithubTokenInvalid(Exception):
    """Raised when the stored access token is rejected by GitHub.
    OAuth App tokens do not expire on a timer and have no refresh
    mechanism (that's a GitHub Apps-only feature) — if this is raised,
    the token has been revoked (by the user or by GitHub) and the only
    fix is the user logging in again. Caller should degrade gracefully
    (serve stale cache) rather than crash.
    """
    pass


async def _run_graphql_query(access_token: str, username: str) -> httpx.Response:
    async with httpx.AsyncClient() as client:
        return await client.post(
            GITHUB_GRAPHQL_URL,
            json={"query": STATS_QUERY, "variables": {"login": username}},
            headers={
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json",
            },
        )


async def fetch_and_cache_stats(user: User, db: Session) -> GithubStatsCache:
    """Fetches fresh GitHub stats for `user` using their stored access token.
    Updates and returns the GithubStatsCache row. Raises GithubTokenInvalid
    if the token is rejected — caller should catch this and fall back to
    serving stale cached data instead of erroring the whole page.
    """
    access_token = decrypt_token(user.encrypted_github_token)

    response = await _run_graphql_query(access_token, user.github_username)

    if response.status_code != 200:
        raise GithubTokenInvalid(
            f"GitHub API call failed with status {response.status_code}"
        )

    data = response.json()
    gh_user = data.get("data", {}).get("user")
    if gh_user is None:
        raise GithubTokenInvalid(f"Unexpected GraphQL response: {data}")

    total_contributions = gh_user["contributionsCollection"]["contributionCalendar"]["totalContributions"]

    repos = gh_user["repositories"]["nodes"]
    languages = [r["primaryLanguage"]["name"] for r in repos if r.get("primaryLanguage")]
    top_languages = sorted(set(languages), key=languages.count, reverse=True)[:5]

    pinned = [
        {
            "name": r["name"],
            "description": r.get("description"),
            "stars": r["stargazerCount"],
            "url": r["url"],
        }
        for r in repos[:6]
    ]

    import json

    cache = db.exec(
        select(GithubStatsCache).where(GithubStatsCache.user_id == user.id)
    ).first()
    if cache is None:
        cache = GithubStatsCache(user_id=user.id)

    cache.total_contributions = total_contributions
    cache.top_languages_json = json.dumps(top_languages)
    cache.pinned_repos_json = json.dumps(pinned)
    cache.last_fetched_at = datetime.utcnow()

    db.add(cache)
    db.commit()
    db.refresh(cache)
    return cache


def is_stale(cache: GithubStatsCache | None) -> bool:
    if cache is None:
        return True
    age = datetime.utcnow() - cache.last_fetched_at
    return age.total_seconds() > STALE_AFTER_HOURS * 3600