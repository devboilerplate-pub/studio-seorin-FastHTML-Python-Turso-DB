from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Any


@dataclass
class User:
    id: str
    email: str
    name: str
    avatar_url: str
    provider: str
    provider_id: str
    is_admin: bool = False
    created_at: str = ""

    def to_session(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "email": self.email,
            "name": self.name,
            "avatar_url": self.avatar_url,
            "provider": self.provider,
            "is_admin": self.is_admin,
        }

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class Work:
    id: str
    slug: str
    title: str
    subtitle: str
    category: str
    year: str
    cover_url: str
    gallery: list[str] = field(default_factory=list)
    body: str = ""
    tags: list[str] = field(default_factory=list)
    client: str = ""
    role: str = ""
    featured: bool = False
    published: bool = True
    like_count: int = 0
    review_count: int = 0
    created_at: str = ""
    updated_at: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class Review:
    id: str
    work_id: str
    user_id: str
    user_name: str
    user_avatar: str
    rating: int
    body: str
    created_at: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class Like:
    id: str
    work_id: str
    user_id: str
    created_at: str = ""


@dataclass
class SiteProfile:
    creator_name: str = "서린"
    creator_name_en: str = "SEO RIN"
    role: str = "Visual Designer / Creative Director"
    tagline: str = "형태보다 온도를, 유행보다 여운을."
    bio: str = (
        "서울을 기반으로 브랜드 아이덴티티, 에디토리얼, 모션, 디지털 경험을 설계합니다. "
        "한 장의 이미지가 오래 남는 이유를 찾고, 그 이유를 시스템으로 만드는 일을 합니다."
    )
    location: str = "Seoul, KR"
    email: str = "hello@seorin.studio"
    instagram: str = "https://instagram.com"
    github: str = "https://github.com"
    hero_kicker: str = "STUDIO SEORIN / EST. 2018"
    statement: str = (
        "나는 visibility가 아니라 presence를 설계한다. "
        "눈에 띄는 것보다, 떠나고 나서도 남는 것을 만든다."
    )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
