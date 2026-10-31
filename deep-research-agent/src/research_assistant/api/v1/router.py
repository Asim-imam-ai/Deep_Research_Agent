"""Secure application endpoints; leave health probe unauthenticated."""

from fastapi import APIRouter, Depends

from research_assistant.api.dependencies.auth import require_api_key
from research_assistant.api.v1.endpoints import analysts, health, interviews, reports, research

router = APIRouter(prefix="/api/v1")
for module in (research, analysts, interviews, reports):
    router.include_router(module.router, dependencies=[Depends(require_api_key)])
router.include_router(health.router)
