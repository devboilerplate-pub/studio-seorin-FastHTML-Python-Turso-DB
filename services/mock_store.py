from __future__ import annotations
import copy
import uuid
from datetime import datetime, timezone
from typing import Optional

from models import User, Work, Review, SiteProfile
from db.seed import PROFILE, WORKS


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


class MockStore:
    def __init__(self):
        self.profile = copy.deepcopy(PROFILE)
        self.works: dict[str, Work] = {w.id: copy.deepcopy(w) for w in WORKS}
        self.users: dict[str, User] = {}
        self.likes: list[tuple[str, str]] = []
        self.reviews: list[Review] = self._seed_reviews()
        self._seed_users()

    def _seed_users(self) -> None:
        admin = User(
            id="u-admin",
            email="seorin@studio.local",
            name="서린",
            avatar_url="",
            provider="mock",
            provider_id="admin",
            is_admin=True,
            created_at="2024-01-01",
        )
        guest = User(
            id="u-guest",
            email="visitor@example.com",
            name="방문객 하나",
            avatar_url="",
            provider="mock",
            provider_id="guest",
            is_admin=False,
            created_at="2025-01-01",
        )
        self.users[admin.id] = admin
        self.users[guest.id] = guest

    def _seed_reviews(self) -> list[Review]:
        samples = [
            Review("r1", "w01", "u-guest", "방문객 하나", "", 5, "패키지를 실제로 만져본 듯한 질감이 화면에도 남습니다.", "2025-04-02"),
            Review("r2", "w01", "u-admin", "서린", "", 5, "내부 메모: 다음 시즌은 겨울 팔레트만으로 가볼 것.", "2025-04-10"),
            Review("r3", "w02", "u-guest", "방문객 하나", "", 4, "타이틀이 영화보다 먼저 밤을 가져갑니다.", "2024-12-01"),
            Review("r4", "w03", "u-guest", "방문객 하나", "", 5, "가구 사이트가 시처럼 읽힙니다.", "2025-07-08"),
            Review("r5", "w06", "u-guest", "방문객 하나", "", 5, "소리를 보기 전에 먼저 듣게 만드는 커버.", "2025-02-20"),
        ]
        return samples

    def get_profile(self) -> SiteProfile:
        return copy.deepcopy(self.profile)

    def update_profile(self, data: dict) -> SiteProfile:
        for key, value in data.items():
            if hasattr(self.profile, key) and value is not None:
                setattr(self.profile, key, value)
        return self.get_profile()

    def _hydrate(self, work: Work) -> Work:
        w = copy.deepcopy(work)
        w.like_count = self.like_count(w.id)
        w.review_count = self.review_count(w.id)
        return w

    def list_works(self, published_only: bool = True, category: str | None = None) -> list[Work]:
        items = list(self.works.values())
        if published_only:
            items = [w for w in items if w.published]
        if category:
            items = [w for w in items if w.category.lower() == category.lower()]
        items.sort(key=lambda w: (w.year, w.created_at), reverse=True)
        return [self._hydrate(w) for w in items]

    def get_work(self, slug: str) -> Optional[Work]:
        for w in self.works.values():
            if w.slug == slug:
                return self._hydrate(w)
        return None

    def get_work_by_id(self, work_id: str) -> Optional[Work]:
        w = self.works.get(work_id)
        return self._hydrate(w) if w else None

    def upsert_work(self, work: Work) -> Work:
        if not work.id:
            work.id = "w" + uuid.uuid4().hex[:8]
        if not work.created_at:
            work.created_at = _now()
        work.updated_at = _now()
        self.works[work.id] = copy.deepcopy(work)
        return self._hydrate(work)

    def delete_work(self, work_id: str) -> None:
        self.works.pop(work_id, None)
        self.likes = [pair for pair in self.likes if pair[0] != work_id]
        self.reviews = [r for r in self.reviews if r.work_id != work_id]

    def categories(self) -> list[str]:
        seen = []
        for w in self.works.values():
            if w.published and w.category and w.category not in seen:
                seen.append(w.category)
        return seen

    def upsert_user(self, user: User) -> User:
        existing = self.get_user_by_provider(user.provider, user.provider_id)
        if existing:
            existing.email = user.email
            existing.name = user.name
            existing.avatar_url = user.avatar_url
            existing.is_admin = user.is_admin or existing.is_admin
            self.users[existing.id] = existing
            return copy.deepcopy(existing)
        if not user.id:
            user.id = "u-" + uuid.uuid4().hex[:10]
        if not user.created_at:
            user.created_at = _now()
        self.users[user.id] = copy.deepcopy(user)
        return copy.deepcopy(user)

    def get_user(self, user_id: str) -> Optional[User]:
        u = self.users.get(user_id)
        return copy.deepcopy(u) if u else None

    def get_user_by_provider(self, provider: str, provider_id: str) -> Optional[User]:
        for u in self.users.values():
            if u.provider == provider and u.provider_id == provider_id:
                return copy.deepcopy(u)
        return None

    def list_users(self) -> list[User]:
        return [copy.deepcopy(u) for u in self.users.values()]

    def toggle_like(self, work_id: str, user_id: str) -> tuple[bool, int]:
        pair = (work_id, user_id)
        if pair in self.likes:
            self.likes.remove(pair)
            return False, self.like_count(work_id)
        self.likes.append(pair)
        return True, self.like_count(work_id)

    def user_liked(self, work_id: str, user_id: str) -> bool:
        return (work_id, user_id) in self.likes

    def like_count(self, work_id: str) -> int:
        seeded = next((w.like_count for w in WORKS if w.id == work_id), 0)
        extra = sum(1 for w, _ in self.likes if w == work_id)
        return seeded + extra

    def add_review(self, review: Review) -> Review:
        if not review.id:
            review.id = "r-" + uuid.uuid4().hex[:8]
        if not review.created_at:
            review.created_at = _now()
        self.reviews.append(copy.deepcopy(review))
        return copy.deepcopy(review)

    def list_reviews(self, work_id: str) -> list[Review]:
        items = [copy.deepcopy(r) for r in self.reviews if r.work_id == work_id]
        items.sort(key=lambda r: r.created_at, reverse=True)
        return items

    def review_count(self, work_id: str) -> int:
        return sum(1 for r in self.reviews if r.work_id == work_id)

    def user_reviewed(self, work_id: str, user_id: str) -> bool:
        return any(r.work_id == work_id and r.user_id == user_id for r in self.reviews)
