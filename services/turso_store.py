from __future__ import annotations
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from models import User, Work, Review, SiteProfile
from db.seed import PROFILE, WORKS


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


class TursoStore:
    def __init__(self, url: str, token: str):
        from libsql_client import create_client_sync

        self.client = create_client_sync(url=url, auth_token=token)
        self._init_schema()
        self._seed_if_empty()

    def _init_schema(self) -> None:
        schema_path = Path(__file__).parent.parent / "db" / "schema.sql"
        sql = schema_path.read_text(encoding="utf-8")
        for stmt in [s.strip() for s in sql.split(";") if s.strip()]:
            self.client.execute(stmt)

    def _seed_if_empty(self) -> None:
        count = self.client.execute("SELECT COUNT(*) AS c FROM works").rows[0][0]
        if count:
            return
        p = PROFILE
        self.client.execute(
            """INSERT INTO site_profile
               (id, creator_name, creator_name_en, role, tagline, bio, location, email, instagram, github, hero_kicker, statement)
               VALUES (1, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            [p.creator_name, p.creator_name_en, p.role, p.tagline, p.bio, p.location,
             p.email, p.instagram, p.github, p.hero_kicker, p.statement],
        )
        for w in WORKS:
            self.client.execute(
                """INSERT INTO works
                   (id, slug, title, subtitle, category, year, cover_url, gallery_json, body, tags_json,
                    client, role, featured, published, created_at, updated_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                [w.id, w.slug, w.title, w.subtitle, w.category, w.year, w.cover_url,
                 json.dumps(w.gallery), w.body, json.dumps(w.tags), w.client, w.role,
                 int(w.featured), int(w.published), w.created_at, w.updated_at],
            )

    def get_profile(self) -> SiteProfile:
        row = self.client.execute("SELECT * FROM site_profile WHERE id = 1").rows
        if not row:
            return SiteProfile()
        r = row[0]
        return SiteProfile(
            creator_name=r[1], creator_name_en=r[2], role=r[3], tagline=r[4], bio=r[5],
            location=r[6], email=r[7], instagram=r[8], github=r[9], hero_kicker=r[10], statement=r[11],
        )

    def update_profile(self, data: dict) -> SiteProfile:
        current = self.get_profile().to_dict()
        current.update({k: v for k, v in data.items() if v is not None and k in current})
        self.client.execute(
            """UPDATE site_profile SET creator_name=?, creator_name_en=?, role=?, tagline=?, bio=?,
               location=?, email=?, instagram=?, github=?, hero_kicker=?, statement=? WHERE id=1""",
            [current["creator_name"], current["creator_name_en"], current["role"], current["tagline"],
             current["bio"], current["location"], current["email"], current["instagram"],
             current["github"], current["hero_kicker"], current["statement"]],
        )
        return self.get_profile()

    def _work_from_row(self, r) -> Work:
        work_id = r[0]
        likes = self.like_count(work_id)
        reviews = self.review_count(work_id)
        return Work(
            id=r[0], slug=r[1], title=r[2], subtitle=r[3], category=r[4], year=r[5],
            cover_url=r[6], gallery=json.loads(r[7] or "[]"), body=r[8],
            tags=json.loads(r[9] or "[]"), client=r[10], role=r[11],
            featured=bool(r[12]), published=bool(r[13]),
            like_count=likes, review_count=reviews,
            created_at=r[14], updated_at=r[15],
        )

    def list_works(self, published_only: bool = True, category: str | None = None) -> list[Work]:
        sql = "SELECT * FROM works"
        args = []
        clauses = []
        if published_only:
            clauses.append("published = 1")
        if category:
            clauses.append("category = ?")
            args.append(category)
        if clauses:
            sql += " WHERE " + " AND ".join(clauses)
        sql += " ORDER BY year DESC, created_at DESC"
        rows = self.client.execute(sql, args).rows
        return [self._work_from_row(r) for r in rows]

    def get_work(self, slug: str) -> Optional[Work]:
        rows = self.client.execute("SELECT * FROM works WHERE slug = ?", [slug]).rows
        return self._work_from_row(rows[0]) if rows else None

    def get_work_by_id(self, work_id: str) -> Optional[Work]:
        rows = self.client.execute("SELECT * FROM works WHERE id = ?", [work_id]).rows
        return self._work_from_row(rows[0]) if rows else None

    def upsert_work(self, work: Work) -> Work:
        if not work.id:
            work.id = "w" + uuid.uuid4().hex[:8]
        if not work.created_at:
            work.created_at = _now()
        work.updated_at = _now()
        self.client.execute(
            """INSERT INTO works
               (id, slug, title, subtitle, category, year, cover_url, gallery_json, body, tags_json,
                client, role, featured, published, created_at, updated_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
               ON CONFLICT(id) DO UPDATE SET
                 slug=excluded.slug, title=excluded.title, subtitle=excluded.subtitle,
                 category=excluded.category, year=excluded.year, cover_url=excluded.cover_url,
                 gallery_json=excluded.gallery_json, body=excluded.body, tags_json=excluded.tags_json,
                 client=excluded.client, role=excluded.role, featured=excluded.featured,
                 published=excluded.published, updated_at=excluded.updated_at""",
            [work.id, work.slug, work.title, work.subtitle, work.category, work.year, work.cover_url,
             json.dumps(work.gallery), work.body, json.dumps(work.tags), work.client, work.role,
             int(work.featured), int(work.published), work.created_at, work.updated_at],
        )
        return self.get_work_by_id(work.id)

    def delete_work(self, work_id: str) -> None:
        self.client.execute("DELETE FROM likes WHERE work_id = ?", [work_id])
        self.client.execute("DELETE FROM reviews WHERE work_id = ?", [work_id])
        self.client.execute("DELETE FROM works WHERE id = ?", [work_id])

    def categories(self) -> list[str]:
        rows = self.client.execute(
            "SELECT DISTINCT category FROM works WHERE published = 1 AND category != '' ORDER BY category"
        ).rows
        return [r[0] for r in rows]

    def upsert_user(self, user: User) -> User:
        existing = self.get_user_by_provider(user.provider, user.provider_id)
        if existing:
            self.client.execute(
                """UPDATE users SET email=?, name=?, avatar_url=?, is_admin=? WHERE id=?""",
                [user.email, user.name, user.avatar_url, int(user.is_admin or existing.is_admin), existing.id],
            )
            return self.get_user(existing.id)
        if not user.id:
            user.id = "u-" + uuid.uuid4().hex[:10]
        if not user.created_at:
            user.created_at = _now()
        self.client.execute(
            """INSERT INTO users (id, email, name, avatar_url, provider, provider_id, is_admin, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            [user.id, user.email, user.name, user.avatar_url, user.provider, user.provider_id,
             int(user.is_admin), user.created_at],
        )
        return self.get_user(user.id)

    def get_user(self, user_id: str) -> Optional[User]:
        rows = self.client.execute("SELECT * FROM users WHERE id = ?", [user_id]).rows
        return self._user_from_row(rows[0]) if rows else None

    def get_user_by_provider(self, provider: str, provider_id: str) -> Optional[User]:
        rows = self.client.execute(
            "SELECT * FROM users WHERE provider = ? AND provider_id = ?", [provider, provider_id]
        ).rows
        return self._user_from_row(rows[0]) if rows else None

    def list_users(self) -> list[User]:
        rows = self.client.execute("SELECT * FROM users ORDER BY created_at DESC").rows
        return [self._user_from_row(r) for r in rows]

    def _user_from_row(self, r) -> User:
        return User(
            id=r[0], email=r[1], name=r[2], avatar_url=r[3], provider=r[4],
            provider_id=r[5], is_admin=bool(r[6]), created_at=r[7],
        )

    def toggle_like(self, work_id: str, user_id: str) -> tuple[bool, int]:
        rows = self.client.execute(
            "SELECT id FROM likes WHERE work_id = ? AND user_id = ?", [work_id, user_id]
        ).rows
        if rows:
            self.client.execute("DELETE FROM likes WHERE id = ?", [rows[0][0]])
            return False, self.like_count(work_id)
        self.client.execute(
            "INSERT INTO likes (id, work_id, user_id, created_at) VALUES (?, ?, ?, ?)",
            ["l-" + uuid.uuid4().hex[:10], work_id, user_id, _now()],
        )
        return True, self.like_count(work_id)

    def user_liked(self, work_id: str, user_id: str) -> bool:
        rows = self.client.execute(
            "SELECT 1 FROM likes WHERE work_id = ? AND user_id = ? LIMIT 1", [work_id, user_id]
        ).rows
        return bool(rows)

    def like_count(self, work_id: str) -> int:
        seeded = next((w.like_count for w in WORKS if w.id == work_id), 0)
        extra = self.client.execute("SELECT COUNT(*) FROM likes WHERE work_id = ?", [work_id]).rows[0][0]
        return seeded + extra

    def add_review(self, review: Review) -> Review:
        if not review.id:
            review.id = "r-" + uuid.uuid4().hex[:8]
        if not review.created_at:
            review.created_at = _now()
        self.client.execute(
            """INSERT INTO reviews (id, work_id, user_id, rating, body, created_at)
               VALUES (?, ?, ?, ?, ?, ?)""",
            [review.id, review.work_id, review.user_id, review.rating, review.body, review.created_at],
        )
        return review

    def list_reviews(self, work_id: str) -> list[Review]:
        rows = self.client.execute(
            """SELECT r.id, r.work_id, r.user_id, u.name, u.avatar_url, r.rating, r.body, r.created_at
               FROM reviews r LEFT JOIN users u ON u.id = r.user_id
               WHERE r.work_id = ? ORDER BY r.created_at DESC""",
            [work_id],
        ).rows
        return [
            Review(
                id=r[0], work_id=r[1], user_id=r[2], user_name=r[3] or "Guest",
                user_avatar=r[4] or "", rating=r[5], body=r[6], created_at=r[7],
            )
            for r in rows
        ]

    def review_count(self, work_id: str) -> int:
        return self.client.execute("SELECT COUNT(*) FROM reviews WHERE work_id = ?", [work_id]).rows[0][0]

    def user_reviewed(self, work_id: str, user_id: str) -> bool:
        rows = self.client.execute(
            "SELECT 1 FROM reviews WHERE work_id = ? AND user_id = ? LIMIT 1", [work_id, user_id]
        ).rows
        return bool(rows)
