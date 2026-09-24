import os
from dataclasses import dataclass, field
from dotenv import load_dotenv

load_dotenv()


def _bool(name: str, default: str = "false") -> bool:
    return os.getenv(name, default).strip().lower() in {"1", "true", "yes", "on"}


def _csv(name: str, default: str = "") -> list[str]:
    raw = os.getenv(name, default)
    return [item.strip().lower() for item in raw.split(",") if item.strip()]


@dataclass(frozen=True)
class Settings:
    use_mock: bool = field(default_factory=lambda: _bool("USE_MOCK", "true"))
    secret_key: str = field(default_factory=lambda: os.getenv("SECRET_KEY", "dev-secret-change-me"))
    site_url: str = field(default_factory=lambda: os.getenv("SITE_URL", "http://localhost:5001").rstrip("/"))
    admin_emails: list[str] = field(default_factory=lambda: _csv(
        "ADMIN_EMAILS", "seorin@studio.local,admin@example.com"
    ))
    turso_url: str = field(default_factory=lambda: os.getenv("TURSO_DATABASE_URL", "").strip())
    turso_token: str = field(default_factory=lambda: os.getenv("TURSO_AUTH_TOKEN", "").strip())
    google_client_id: str = field(default_factory=lambda: os.getenv("GOOGLE_CLIENT_ID", "").strip())
    google_client_secret: str = field(default_factory=lambda: os.getenv("GOOGLE_CLIENT_SECRET", "").strip())
    github_client_id: str = field(default_factory=lambda: os.getenv("GITHUB_CLIENT_ID", "").strip())
    github_client_secret: str = field(default_factory=lambda: os.getenv("GITHUB_CLIENT_SECRET", "").strip())

    @property
    def use_turso(self) -> bool:
        return (not self.use_mock) and bool(self.turso_url)

    @property
    def google_ready(self) -> bool:
        return bool(self.google_client_id and self.google_client_secret)

    @property
    def github_ready(self) -> bool:
        return bool(self.github_client_id and self.github_client_secret)


settings = Settings()
