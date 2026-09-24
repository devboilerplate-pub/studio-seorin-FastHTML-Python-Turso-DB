from __future__ import annotations
from authlib.integrations.starlette_client import OAuth
from starlette.requests import Request

from config import settings
from models import User
from services.interfaces import Store


class AuthServiceImpl:
    def __init__(self, store: Store):
        self.store = store
        self.oauth = OAuth()
        if settings.google_ready:
            self.oauth.register(
                name="google",
                client_id=settings.google_client_id,
                client_secret=settings.google_client_secret,
                server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
                client_kwargs={"scope": "openid email profile"},
            )
        if settings.github_ready:
            self.oauth.register(
                name="github",
                client_id=settings.github_client_id,
                client_secret=settings.github_client_secret,
                access_token_url="https://github.com/login/oauth/access_token",
                authorize_url="https://github.com/login/oauth/authorize",
                api_base_url="https://api.github.com/",
                client_kwargs={"scope": "user:email"},
            )

    def providers_ready(self) -> dict[str, bool]:
        return {
            "google": settings.google_ready,
            "github": settings.github_ready,
            "mock": settings.use_mock or not (settings.google_ready or settings.github_ready),
        }

    def login_url(self, provider: str, redirect_uri: str) -> str:
        return f"/auth/login/{provider}?next={redirect_uri}"

    async def authorize_redirect(self, request: Request, provider: str, redirect_uri: str):
        client = self.oauth.create_client(provider)
        if client is None:
            raise ValueError(f"provider {provider} is not configured")
        return await client.authorize_redirect(request, redirect_uri)

    async def handle_callback(self, provider: str, request: Request) -> User:
        client = self.oauth.create_client(provider)
        token = await client.authorize_access_token(request)
        if provider == "google":
            info = token.get("userinfo") or {}
            email = (info.get("email") or "").lower()
            name = info.get("name") or email.split("@")[0]
            avatar = info.get("picture") or ""
            pid = info.get("sub") or email
        else:
            resp = await client.get("user", token=token)
            data = resp.json()
            email = (data.get("email") or "").lower()
            if not email:
                emails = await client.get("user/emails", token=token)
                items = emails.json() if emails else []
                primary = next((e for e in items if e.get("primary")), items[0] if items else {})
                email = (primary.get("email") or f"gh-{data.get('id')}@users.noreply.github.com").lower()
            name = data.get("name") or data.get("login") or email.split("@")[0]
            avatar = data.get("avatar_url") or ""
            pid = str(data.get("id"))
        user = User(
            id="",
            email=email,
            name=name,
            avatar_url=avatar,
            provider=provider,
            provider_id=str(pid),
            is_admin=email in settings.admin_emails,
        )
        return self.store.upsert_user(user)

    def mock_login(self, provider: str, as_admin: bool = False) -> User:
        if as_admin:
            user = User(
                id="u-admin",
                email="seorin@studio.local",
                name="서린",
                avatar_url="",
                provider="mock",
                provider_id="admin",
                is_admin=True,
            )
        else:
            label = "Google" if provider == "google" else "GitHub"
            user = User(
                id="",
                email=f"visitor-{provider}@example.com",
                name=f"{label} 방문객",
                avatar_url="",
                provider=f"mock-{provider}",
                provider_id=provider,
                is_admin=False,
            )
        user.is_admin = user.is_admin or user.email.lower() in settings.admin_emails
        return self.store.upsert_user(user)
