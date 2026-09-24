from fasthtml.common import *
from starlette.requests import Request
from starlette.responses import RedirectResponse

from components import page_shell, flash_banner
from models import Work
from services.container import get_store, current_user


def _require_admin(request: Request):
    user = current_user(request)
    if not user:
        return None, RedirectResponse("/auth/login", status_code=303)
    if not user.is_admin:
        return None, RedirectResponse("/", status_code=303)
    return user, None


def _bool_field(form, name: str) -> bool:
    val = form.get(name)
    return val in {"1", "true", "on", "yes"}


def register(app):
    store = get_store()

    @app.get("/admin")
    def admin_home(request: Request):
        user, denied = _require_admin(request)
        if denied:
            return denied
        profile = store.get_profile()
        works = store.list_works(published_only=False)
        users = store.list_users()
        flash = request.session.pop("flash", None)
        rows = [
            Tr(
                Td(w.year),
                Td(A(w.title, href=f"/works/{w.slug}")),
                Td(w.category),
                Td("공개" if w.published else "초안"),
                Td(str(w.like_count)),
                Td(
                    A("Edit", href=f"/admin/works/{w.id}", cls="table-link"),
                    Form(
                        Button("Delete", type="submit", cls="table-danger"),
                        action=f"/admin/works/{w.id}/delete",
                        method="post",
                        cls="inline-form",
                    ),
                    cls="table-actions",
                ),
            )
            for w in works
        ]
        return page_shell(
            "Admin",
            user,
            profile,
            flash_banner(flash),
            Section(
                P("Backstage", cls="page-kicker"),
                H1("Content desk", cls="page-title"),
                P("작업, 프로필, 방문객. 목업과 실제 DB가 같은 화면을 씁니다.", cls="page-lead"),
                cls="page-intro",
            ),
            Section(
                Div(
                    Article(Strong(str(len(works))), P("Works"), cls="stat"),
                    Article(Strong(str(len(users))), P("Visitors"), cls="stat"),
                    Article(Strong(str(sum(w.like_count for w in works))), P("Likes"), cls="stat"),
                    Article(Strong(str(sum(w.review_count for w in works))), P("Notes"), cls="stat"),
                    cls="stat-row",
                ),
                cls="section",
            ),
            Section(
                Div(
                    H2("Works", cls="sec-title"),
                    A("New work", href="/admin/works/new", cls="btn btn-solid"),
                    cls="sec-head",
                ),
                Table(
                    Thead(Tr(Th("Year"), Th("Title"), Th("Category"), Th("Status"), Th("Likes"), Th(""))),
                    Tbody(*rows),
                    cls="admin-table",
                ),
                cls="section",
            ),
            Section(
                H2("Studio profile", cls="sec-title"),
                Form(
                    Div(
                        Label("Name", For="creator_name"),
                        Input(name="creator_name", id="creator_name", value=profile.creator_name),
                        Label("Name EN", For="creator_name_en"),
                        Input(name="creator_name_en", id="creator_name_en", value=profile.creator_name_en),
                        Label("Role", For="role"),
                        Input(name="role", id="role", value=profile.role),
                        Label("Tagline", For="tagline"),
                        Input(name="tagline", id="tagline", value=profile.tagline),
                        Label("Hero kicker", For="hero_kicker"),
                        Input(name="hero_kicker", id="hero_kicker", value=profile.hero_kicker),
                        Label("Email", For="email"),
                        Input(name="email", id="email", value=profile.email),
                        Label("Location", For="location"),
                        Input(name="location", id="location", value=profile.location),
                        Label("Instagram", For="instagram"),
                        Input(name="instagram", id="instagram", value=profile.instagram),
                        Label("GitHub", For="github"),
                        Input(name="github", id="github", value=profile.github),
                        cls="form-grid",
                    ),
                    Label("Bio", For="bio"),
                    Textarea(profile.bio, name="bio", id="bio", rows="4"),
                    Label("Statement", For="statement"),
                    Textarea(profile.statement, name="statement", id="statement", rows="3"),
                    Button("Save profile", type="submit", cls="btn btn-solid"),
                    action="/admin/profile",
                    method="post",
                    cls="admin-form",
                ),
                cls="section",
            ),
            path="/admin",
        )

    @app.post("/admin/profile")
    async def save_profile(request: Request):
        user, denied = _require_admin(request)
        if denied:
            return denied
        form = await request.form()
        keys = [
            "creator_name", "creator_name_en", "role", "tagline", "bio",
            "location", "email", "instagram", "github", "hero_kicker", "statement",
        ]
        store.update_profile({k: form.get(k, "") for k in keys})
        request.session["flash"] = "프로필이 저장되었습니다."
        return RedirectResponse("/admin", status_code=303)

    def _work_form(work: Work | None, action: str):
        w = work or Work(
            id="", slug="", title="", subtitle="", category="", year="", cover_url="/static/img/work-1.svg",
        )
        return Form(
            Div(
                Label("Title", For="title"),
                Input(name="title", id="title", value=w.title, required=True),
                Label("Slug", For="slug"),
                Input(name="slug", id="slug", value=w.slug, required=True),
                Label("Subtitle", For="subtitle"),
                Input(name="subtitle", id="subtitle", value=w.subtitle),
                Label("Category", For="category"),
                Input(name="category", id="category", value=w.category),
                Label("Year", For="year"),
                Input(name="year", id="year", value=w.year),
                Label("Client", For="client"),
                Input(name="client", id="client", value=w.client),
                Label("Role", For="role"),
                Input(name="role", id="role", value=w.role),
                Label("Cover URL", For="cover_url"),
                Input(name="cover_url", id="cover_url", value=w.cover_url),
                Label("Gallery (comma)", For="gallery"),
                Input(name="gallery", id="gallery", value=",".join(w.gallery)),
                Label("Tags (comma)", For="tags"),
                Input(name="tags", id="tags", value=",".join(w.tags)),
                cls="form-grid",
            ),
            Label("Body", For="body"),
            Textarea(w.body, name="body", id="body", rows="8"),
            Div(
                Label(
                    Input(type="checkbox", name="featured", checked="checked" if w.featured else None),
                    " Featured",
                ),
                Label(
                    Input(type="checkbox", name="published", checked="checked" if (w.published or not work) else None),
                    " Published",
                ),
                cls="check-row",
            ),
            Button("Save work", type="submit", cls="btn btn-solid"),
            action=action,
            method="post",
            cls="admin-form",
        )

    @app.get("/admin/works/new")
    def new_work(request: Request):
        user, denied = _require_admin(request)
        if denied:
            return denied
        profile = store.get_profile()
        return page_shell(
            "New work",
            user,
            profile,
            Section(
                A("← Desk", href="/admin", cls="back-link"),
                H1("New work", cls="page-title"),
                _work_form(None, "/admin/works/new"),
                cls="page-intro",
            ),
            path="/admin",
        )

    @app.post("/admin/works/new")
    async def create_work(request: Request):
        user, denied = _require_admin(request)
        if denied:
            return denied
        form = await request.form()
        work = Work(
            id="",
            slug=form.get("slug", "").strip(),
            title=form.get("title", "").strip(),
            subtitle=form.get("subtitle", "").strip(),
            category=form.get("category", "").strip(),
            year=form.get("year", "").strip(),
            cover_url=form.get("cover_url", "").strip() or "/static/img/work-1.svg",
            gallery=[g.strip() for g in (form.get("gallery") or "").split(",") if g.strip()],
            body=form.get("body", ""),
            tags=[t.strip() for t in (form.get("tags") or "").split(",") if t.strip()],
            client=form.get("client", "").strip(),
            role=form.get("role", "").strip(),
            featured=_bool_field(form, "featured"),
            published=_bool_field(form, "published"),
        )
        store.upsert_work(work)
        request.session["flash"] = "작업이 추가되었습니다."
        return RedirectResponse("/admin", status_code=303)

    @app.get("/admin/works/{work_id}")
    def edit_work(request: Request, work_id: str):
        user, denied = _require_admin(request)
        if denied:
            return denied
        work = store.get_work_by_id(work_id)
        if not work:
            return RedirectResponse("/admin", status_code=303)
        profile = store.get_profile()
        return page_shell(
            f"Edit {work.title}",
            user,
            profile,
            Section(
                A("← Desk", href="/admin", cls="back-link"),
                H1(work.title, cls="page-title"),
                _work_form(work, f"/admin/works/{work.id}"),
                cls="page-intro",
            ),
            path="/admin",
        )

    @app.post("/admin/works/{work_id}")
    async def update_work(request: Request, work_id: str):
        user, denied = _require_admin(request)
        if denied:
            return denied
        existing = store.get_work_by_id(work_id)
        if not existing:
            return RedirectResponse("/admin", status_code=303)
        form = await request.form()
        existing.title = form.get("title", "").strip()
        existing.slug = form.get("slug", "").strip()
        existing.subtitle = form.get("subtitle", "").strip()
        existing.category = form.get("category", "").strip()
        existing.year = form.get("year", "").strip()
        existing.cover_url = form.get("cover_url", "").strip() or existing.cover_url
        existing.gallery = [g.strip() for g in (form.get("gallery") or "").split(",") if g.strip()]
        existing.body = form.get("body", "")
        existing.tags = [t.strip() for t in (form.get("tags") or "").split(",") if t.strip()]
        existing.client = form.get("client", "").strip()
        existing.role = form.get("role", "").strip()
        existing.featured = _bool_field(form, "featured")
        existing.published = _bool_field(form, "published")
        store.upsert_work(existing)
        request.session["flash"] = "작업이 저장되었습니다."
        return RedirectResponse("/admin", status_code=303)

    @app.post("/admin/works/{work_id}/delete")
    async def delete_work(request: Request, work_id: str):
        user, denied = _require_admin(request)
        if denied:
            return denied
        store.delete_work(work_id)
        request.session["flash"] = "작업이 삭제되었습니다."
        return RedirectResponse("/admin", status_code=303)
