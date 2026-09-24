from fasthtml.common import *
from starlette.middleware.sessions import SessionMiddleware
from starlette.staticfiles import StaticFiles
import os

from config import settings
from routes import pages, auth_routes, admin as admin_routes


def create_app():
    app = FastHTML(
        hdrs=[],
        pico=False,
        default_hdrs=False,
        secret_key=settings.secret_key,
        key_fname="/tmp/.sesskey",
        exception_handlers={
            404: lambda req, exc: Html(
                Head(Title("404"), Link(rel="stylesheet", href="/static/css/style.css")),
                Body(
                    Main(
                        P("404", cls="page-kicker"),
                        H1("This page has left the room."),
                        A("Return to studio", href="/", cls="btn btn-solid"),
                        cls="page-intro",
                        style="min-height:70vh;display:flex;flex-direction:column;justify-content:center;",
                    ),
                    cls="body-root",
                ),
            )
        },
    )
    app.add_middleware(SessionMiddleware, secret_key=settings.secret_key, max_age=60 * 60 * 24 * 14)
    current_dir = os.path.dirname(os.path.realpath(__file__))
    app.mount("/static", StaticFiles(directory=os.path.join(current_dir, "static")), name="static")
    pages.register(app)
    auth_routes.register(app)
    admin_routes.register(app)
    return app


app = create_app()
serve = app

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=5001, reload=False)
