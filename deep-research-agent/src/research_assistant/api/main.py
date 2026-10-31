"""FastAPI application factory."""

from fastapi import FastAPI

from research_assistant.api.middleware.request_context import RequestContextMiddleware
from research_assistant.api.v1.router import router
from research_assistant.core.lifespan import lifespan
from research_assistant.observability.tracing import configure_tracing


def create_app() -> FastAPI:
    configure_tracing()
    app = FastAPI(title="LangGraph Research Assistant", version="0.3.0", lifespan=lifespan)
    app.add_middleware(RequestContextMiddleware)
    app.include_router(router)
    return app


app = create_app()
