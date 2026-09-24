from __future__ import annotations
from functools import lru_cache
from starlette.requests import Request

from config import settings
from models import User
from services.mock_store import MockStore
from services.auth import AuthServiceImpl


@lru_cache(maxsize=1)
def get_store():
    if settings.use_turso:
        from services.turso_store import TursoStore
        return TursoStore(settings.turso_url, settings.turso_token)
    return MockStore()


@lru_cache(maxsize=1)
def get_auth() -> AuthServiceImpl:
    return AuthServiceImpl(get_store())


def current_user(request: Request) -> User | None:
    data = request.session.get("user")
    if not data:
        return None
    return User(
        id=data.get("id", ""),
        email=data.get("email", ""),
        name=data.get("name", ""),
        avatar_url=data.get("avatar_url", ""),
        provider=data.get("provider", ""),
        provider_id="",
        is_admin=bool(data.get("is_admin")),
    )
