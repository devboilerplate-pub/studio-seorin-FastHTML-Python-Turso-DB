from fasthtml.common import *
from models import User, Work, SiteProfile


NAV_ITEMS = [
    ("/", "Index"),
    ("/works", "Works"),
    ("/about", "About"),
]


def initials(name: str) -> str:
    parts = [p for p in (name or "").split() if p]
    if not parts:
        return "SR"
    if len(parts[0]) >= 2 and not parts[0].isascii():
        return parts[0][:1]
    return "".join(p[0] for p in parts[:2]).upper()


def site_head(title: str, extra=None):
    tags = [
        Title(f"{title} — Studio Seorin"),
        Meta(charset="utf-8"),
        Meta(name="viewport", content="width=device-width, initial-scale=1"),
        Meta(name="description", content="Studio Seorin — visual design, identity, motion, editorial."),
        Link(rel="preconnect", href="https://fonts.googleapis.com"),
        Link(rel="preconnect", href="https://fonts.gstatic.com", crossorigin=""),
        Link(
            rel="stylesheet",
            href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,400;0,500;0,600;1,400;1,500&family=Syne:wght@500;600;700;800&family=IBM+Plex+Sans+KR:wght@300;400;500;600&display=swap",
        ),
        Link(rel="stylesheet", href="/static/css/style.css"),
        Link(rel="icon", href="/static/img/favicon.svg", type="image/svg+xml"),
    ]
    if extra:
        tags.extend(extra if isinstance(extra, list) else [extra])
    return tags


def nav_bar(user: User | None, path: str = "/"):
    links = []
    for href, label in NAV_ITEMS:
        cls = "nav-link is-active" if (path == href or (href != "/" and path.startswith(href))) else "nav-link"
        links.append(A(label, href=href, cls=cls))
    auth_slot = []
    if user:
        auth_slot.append(
            Div(
                Span(initials(user.name), cls="avatar-mark"),
                Span(user.name, cls="nav-user-name"),
                A("로그아웃", href="/auth/logout", cls="nav-link subtle"),
                *([A("Admin", href="/admin", cls="nav-link")] if user.is_admin else []),
                cls="nav-user",
            )
        )
    else:
        auth_slot.append(A("Enter", href="/auth/login", cls="nav-cta"))
    return Header(
        A(
            Span("STUDIO", cls="brand-kicker"),
            Span("SEORIN", cls="brand-name"),
            href="/",
            cls="brand",
        ),
        Nav(*links, cls="nav-links"),
        Div(*auth_slot, cls="nav-end"),
        Button("Menu", type="button", cls="nav-toggle", id="navToggle", **{"aria-label": "menu"}),
        cls="site-header",
        id="siteHeader",
    )


def site_footer(profile: SiteProfile):
    return Footer(
        Div(
            Div(
                P("Studio Seorin", cls="foot-brand"),
                P(profile.tagline, cls="foot-tag"),
                cls="foot-col",
            ),
            Div(
                P("Contact", cls="foot-label"),
                A(profile.email, href=f"mailto:{profile.email}"),
                P(profile.location),
                cls="foot-col",
            ),
            Div(
                P("Elsewhere", cls="foot-label"),
                A("Instagram", href=profile.instagram, target="_blank", rel="noreferrer"),
                A("GitHub", href="https://github.com", target="_blank", rel="noreferrer"),
                cls="foot-col",
            ),
            Div(
                P("Colophon", cls="foot-label"),
                P("FastHTML · Turso · Authlib"),
                P("Designed as presence, not noise."),
                cls="foot-col",
            ),
            cls="foot-grid",
        ),
        Div(
            P("© 2026 Studio Seorin. All rights reserved."),
            A("Top", href="#top", cls="to-top"),
            cls="foot-bar",
        ),
        cls="site-footer",
    )


def page_shell(title: str, user: User | None, profile: SiteProfile, *body, path="/", extra_head=None):
    children = [item for item in body if item is not None]
    return Html(
        Head(*site_head(title, extra_head)),
        Body(
            Div(id="top"),
            nav_bar(user, path),
            Div(
                *children,
                cls="page-main",
            ),
            site_footer(profile),
            Script(src="/static/js/app.js"),
            cls="body-root",
            data_path=path,
        ),
        lang="ko",
    )


def work_card(work: Work, featured: bool = False):
    cls = "work-card is-featured" if featured else "work-card"
    return A(
        Div(
            Img(src=work.cover_url, alt=work.title, cls="work-cover"),
            Span(work.year, cls="work-year"),
            cls="work-media",
        ),
        Div(
            P(work.category, cls="work-cat"),
            H3(work.title, cls="work-title"),
            P(work.subtitle, cls="work-sub"),
            Div(
                Span(f"{work.like_count} likes", cls="meta-chip"),
                Span(f"{work.review_count} notes", cls="meta-chip"),
                cls="work-meta",
            ),
            cls="work-copy",
        ),
        href=f"/works/{work.slug}",
        cls=cls,
    )


def flash_banner(message: str | None, kind: str = "ok"):
    if not message:
        return None
    return Div(message, cls=f"flash flash-{kind}")


def stars(rating: int):
    filled = "●" * int(rating)
    empty = "○" * (5 - int(rating))
    return Span(filled + empty, cls="stars", **{"aria-label": f"{rating} / 5"})
