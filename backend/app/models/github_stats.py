from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field



class GithubStatsCache(SQLModel, table=True):
    """Cached GitHub stats for a user, refreshed stale-on-view.
 
    One row per user. last_fetched_at drives the staleness check
    in the profile GET endpoint.
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", unique=True, index=True)
 
    total_contributions: int = 0
    top_languages_json: str = "[]"   # JSON-encoded list, kept simple for Phase 1
    pinned_repos_json: str = "[]"    # JSON-encoded list of {name, description, stars, url}
 
    last_fetched_at: datetime = Field(default_factory=datetime.utcnow)
