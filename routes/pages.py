from fasthtml.common import *
from starlette.requests import Request
from starlette.responses import RedirectResponse

from components import page_shell, work_card, flash_banner, stars
from models import Review
from services.container import get_store, current_user


def register(app):
    store = get_store()

    @app.get("/")
    def home(request: Request):
        user = current_user(request)
        profile = store.get_profile()
        works = store.list_works()
        featured = [w for w in works if w.featured][:3]
        rest = [w for w in works if w not in featured][:3]
        return page_shell(
            "Index",
            user,
            profile,
            Section(
                P(profile.hero_kicker, cls="hero-kicker"),
                H1(
                    Span("형태보다 온도를,", cls="line"),
                    Span("유행보다 여운을.", cls="line italic"),
                    cls="hero-title",
                ),
                P(profile.bio, cls="hero-bio"),
                Div(
                    A("Selected Works", href="/works", cls="btn btn-solid"),
                    A("Studio Notes", href="/about", cls="btn btn-ghost"),
                    cls="hero-actions",
                ),
                Div(
                    Span("01  Identity"),
                    Span("02  Motion"),
                    Span("03  Editorial"),
                    Span("04  Spatial"),
                    cls="hero-disciplines",
                ),
                cls="hero",
            ),
            Section(
                Div(
                    H2("Selected", cls="sec-title"),
                    A("All works →", href="/works", cls="sec-link"),
                    cls="sec-head",
                ),
                Div(*[work_card(w, featured=True) for w in featured], cls="featured-grid"),
                cls="section",
            ),
            Section(
                Div(
                    Div(
                        P("Manifesto", cls="label"),
                        H2(profile.statement, cls="manifesto"),
                        cls="manifesto-copy",
                    ),
                    Div(
                        Img(src="/static/img/portrait.svg", alt="Studio mark", cls="portrait"),
                        P(f"{profile.creator_name}  {profile.creator_name_en}", cls="portrait-cap"),
                        P(profile.role, cls="portrait-role"),
                        cls="manifesto-side",
                    ),
                    cls="manifesto-grid",
                ),
                cls="section section-ink",
            ),
            Section(
                Div(
                    H2("Also", cls="sec-title"),
                    cls="sec-head",
                ),
                Div(*[work_card(w) for w in rest], cls="work-grid"),
                cls="section",
            ),
            path="/",
        )

    @app.get("/works")
    def works(request: Request, category: str = ""):
        user = current_user(request)
        profile = store.get_profile()
        cats = store.categories()
        items = store.list_works(category=category or None)
        chips = [A("All", href="/works", cls="chip" + (" is-on" if not category else ""))]
        for c in cats:
            chips.append(A(c, href=f"/works?category={c}", cls="chip" + (" is-on" if category == c else "")))
        return page_shell(
            "Works",
            user,
            profile,
            Section(
                P("Archive", cls="page-kicker"),
                H1("Works", cls="page-title"),
                P("브랜드, 영상, 지면, 공간. 남는 온도를 기준으로 고른 작업들.", cls="page-lead"),
                Div(*chips, cls="chip-row"),
                cls="page-intro",
            ),
            Section(
                Div(*[work_card(w) for w in items], cls="work-grid dense") if items else P("아직 공개된 작업이 없습니다.", cls="empty"),
                cls="section",
            ),
            path="/works",
        )

    @app.get("/works/{slug}")
    def work_detail(request: Request, slug: str):
        user = current_user(request)
        profile = store.get_profile()
        work = store.get_work(slug)
        if not work:
            return page_shell(
                "Not found",
                user,
                profile,
                Section(H1("Work not found"), A("Archive로 돌아가기", href="/works", cls="btn btn-solid"), cls="page-intro"),
                path="/works",
            )
        reviews = store.list_reviews(work.id)
        liked = store.user_liked(work.id, user.id) if user else False
        reviewed = store.user_reviewed(work.id, user.id) if user else False
        flash = request.session.pop("flash", None)

        gallery = [
            Img(src=src, alt=f"{work.title} still {i+1}", cls="gallery-img")
            for i, src in enumerate(work.gallery or [work.cover_url])
        ]

        like_form = Form(
            Input(type="hidden", name="work_id", value=work.id),
            Button(
                "Liked" if liked else "Like this work",
                Span(str(work.like_count), cls="count-pill"),
                type="submit",
                cls="btn " + ("btn-solid" if liked else "btn-ghost"),
            ),
            action="/api/like",
            method="post",
            cls="inline-form",
        ) if user else A("로그인하고 좋아요", href="/auth/login", cls="btn btn-ghost")

        if user and not reviewed:
            review_block = Form(
                Fieldset(
                    Legend("Leave a note"),
                    Label("Rating", For="rating"),
                    Select(
                        *[Option(str(i), value=str(i), selected="selected" if i == 5 else None) for i in range(5, 0, -1)],
                        name="rating",
                        id="rating",
                    ),
                    Label("Note", For="body"),
                    Textarea(name="body", id="body", rows="4", required=True, placeholder="이 작업이 남긴 온도를 한 줄로."),
                    Button("Publish note", type="submit", cls="btn btn-solid"),
                    Input(type="hidden", name="work_id", value=work.id),
                    Input(type="hidden", name="slug", value=work.slug),
                ),
                action="/api/review",
                method="post",
                cls="review-form",
            )
        elif not user:
            review_block = P(
                A("로그인", href="/auth/login", cls="text-link"),
                " 후 리뷰를 남길 수 있습니다.",
                cls="hint",
            )
        else:
            review_block = P("이미 이 작업에 노트를 남겼습니다.", cls="hint")

        review_list = [
            Article(
                Div(
                    Strong(r.user_name),
                    stars(r.rating),
                    Span(r.created_at, cls="muted"),
                    cls="review-head",
                ),
                P(r.body),
                cls="review-card",
            )
            for r in reviews
        ]

        return page_shell(
            work.title,
            user,
            profile,
            flash_banner(flash),
            Section(
                A("← Archive", href="/works", cls="back-link"),
                P(f"{work.category}  /  {work.year}", cls="page-kicker"),
                H1(work.title, cls="page-title display"),
                P(work.subtitle, cls="page-lead"),
                Div(*gallery, cls="gallery"),
                cls="page-intro",
            ),
            Section(
                Div(
                    Div(
                        P(work.body, cls="body-copy"),
                        Div(like_form, cls="like-row"),
                        cls="detail-main",
                    ),
                    Aside(
                        Div(Span("Client"), Strong(work.client), cls="spec"),
                        Div(Span("Role"), Strong(work.role), cls="spec"),
                        Div(Span("Year"), Strong(work.year), cls="spec"),
                        Div(Span("Tags"), P(" · ".join(work.tags), cls="tag-line"), cls="spec"),
                        cls="spec-card",
                    ),
                    cls="detail-grid",
                ),
                cls="section",
            ),
            Section(
                H2("Notes", cls="sec-title"),
                review_block,
                Div(*review_list, cls="review-list") if review_list else P("아직 노트가 없습니다. 첫 문장을 남겨 주세요.", cls="empty"),
                cls="section",
            ),
            path="/works",
        )

    @app.get("/about")
    def about(request: Request):
        user = current_user(request)
        profile = store.get_profile()
        return page_shell(
            "About",
            user,
            profile,
            Section(
                P("Studio", cls="page-kicker"),
                H1(profile.creator_name, cls="page-title"),
                P(profile.creator_name_en + "  ·  " + profile.role, cls="page-lead"),
                cls="page-intro",
            ),
            Section(
                Div(
                    Img(src="/static/img/portrait.svg", alt="Portrait mark", cls="about-portrait"),
                    Div(
                        P(profile.bio, cls="body-copy"),
                        P(profile.statement, cls="pull-quote"),
                        Ul(
                            Li(f"Based in {profile.location}"),
                            Li(A(profile.email, href=f"mailto:{profile.email}")),
                            Li(A("Instagram", href=profile.instagram, target="_blank", rel="noreferrer")),
                            cls="about-list",
                        ),
                        cls="about-copy",
                    ),
                    cls="about-grid",
                ),
                cls="section",
            ),
            Section(
                H2("Services", cls="sec-title"),
                Div(
                    Article(H3("Identity"), P("로고를 만드는 일이 아니라, 브랜드가 말하는 속도를 정하는 일."), cls="svc"),
                    Article(H3("Editorial"), P("읽히는 리듬. 여백이 문장보다 먼저 설득하는 지면."), cls="svc"),
                    Article(H3("Motion"), P("컷의 길이로 호흡을 설계하고, 타이포로 시간을 자른다."), cls="svc"),
                    Article(H3("Digital"), P("클릭보다 머무름. 화면을 공간처럼 다루는 웹."), cls="svc"),
                    cls="svc-grid",
                ),
                cls="section",
            ),
            path="/about",
        )

    @app.post("/api/like")
    async def like(request: Request):
        user = current_user(request)
        if not user:
            return RedirectResponse("/auth/login", status_code=303)
        form = await request.form()
        work_id = form.get("work_id")
        work = store.get_work_by_id(work_id)
        if not work:
            return RedirectResponse("/works", status_code=303)
        store.toggle_like(work.id, user.id)
        return RedirectResponse(f"/works/{work.slug}", status_code=303)

    @app.post("/api/review")
    async def review(request: Request):
        user = current_user(request)
        if not user:
            return RedirectResponse("/auth/login", status_code=303)
        form = await request.form()
        work_id = form.get("work_id")
        slug = form.get("slug")
        body = (form.get("body") or "").strip()
        try:
            rating = int(form.get("rating") or 5)
        except ValueError:
            rating = 5
        rating = max(1, min(5, rating))
        work = store.get_work_by_id(work_id)
        if not work:
            return RedirectResponse("/works", status_code=303)
        if store.user_reviewed(work.id, user.id):
            request.session["flash"] = "이미 노트를 남겼습니다."
            return RedirectResponse(f"/works/{work.slug}", status_code=303)
        if not body:
            request.session["flash"] = "노트를 입력해 주세요."
            return RedirectResponse(f"/works/{work.slug}", status_code=303)
        store.add_review(Review(
            id="",
            work_id=work.id,
            user_id=user.id,
            user_name=user.name,
            user_avatar=user.avatar_url,
            rating=rating,
            body=body,
        ))
        request.session["flash"] = "노트가 등록되었습니다."
        return RedirectResponse(f"/works/{slug or work.slug}", status_code=303)
