from fasthtml.common import *
from starlette.requests import Request
from starlette.responses import RedirectResponse

from components import page_shell
from config import settings
from services.container import get_store, get_auth, current_user


def register(app):
    store = get_store()
    auth = get_auth()

    @app.get("/auth/login")
    def login_page(request: Request):
        user = current_user(request)
        if user:
            return RedirectResponse("/", status_code=303)
        profile = store.get_profile()
        ready = auth.providers_ready()
        buttons = []
        if ready.get("google"):
            buttons.append(A("Continue with Google", href="/auth/login/google", cls="btn btn-solid oauth google"))
        if ready.get("github"):
            buttons.append(A("Continue with GitHub", href="/auth/login/github", cls="btn btn-solid oauth github"))
        if ready.get("mock"):
            buttons.extend([
                P("목업 모드 — 실제 OAuth 키가 없으면 아래 버튼으로 흐름을 확인합니다.", cls="hint"),
                A("Google 방문객으로 입장", href="/auth/mock/google", cls="btn btn-ghost"),
                A("GitHub 방문객으로 입장", href="/auth/mock/github", cls="btn btn-ghost"),
                A("관리자(서린)로 입장", href="/auth/mock/admin", cls="btn btn-ghost"),
            ])
        return page_shell(
            "Enter",
            user,
            profile,
            Section(
                P("Threshold", cls="page-kicker"),
                H1("Enter the studio", cls="page-title"),
                P("좋아요와 노트는 로그인한 손님만 남길 수 있습니다. 관리자는 콘텐츠를 다듬습니다.", cls="page-lead"),
                Div(*buttons, cls="auth-stack"),
                cls="page-intro auth-intro",
            ),
            path="/auth/login",
        )

    @app.get("/auth/login/{provider}")
    async def login_start(request: Request, provider: str):
        if provider not in {"google", "github"}:
            return RedirectResponse("/auth/login", status_code=303)
        ready = auth.providers_ready()
        if not ready.get(provider):
            return RedirectResponse(f"/auth/mock/{provider}", status_code=303)
        redirect_uri = f"{settings.site_url}/auth/callback/{provider}"
        return await auth.authorize_redirect(request, provider, redirect_uri)

    @app.get("/auth/callback/{provider}")
    async def login_callback(request: Request, provider: str):
        if provider not in {"google", "github"}:
            return RedirectResponse("/auth/login", status_code=303)
        try:
            user = await auth.handle_callback(provider, request)
        except Exception:
            request.session["flash"] = "로그인에 실패했습니다. 목업 모드로 전환하거나 키를 확인해 주세요."
            return RedirectResponse("/auth/login", status_code=303)
        request.session["user"] = user.to_session()
        dest = "/admin" if user.is_admin else "/"
        return RedirectResponse(dest, status_code=303)

    @app.get("/auth/mock/{kind}")
    def mock_login(request: Request, kind: str):
        as_admin = kind == "admin"
        provider = "google" if kind in {"google", "admin"} else "github"
        user = auth.mock_login(provider, as_admin=as_admin)
        request.session["user"] = user.to_session()
        return RedirectResponse("/admin" if user.is_admin else "/", status_code=303)

    @app.get("/auth/logout")
    def logout(request: Request):
        request.session.clear()
        return RedirectResponse("/", status_code=303)
