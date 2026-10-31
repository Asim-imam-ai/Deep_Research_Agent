"""Startup uses migrations; no automatic schema creation in request workers."""

from contextlib import asynccontextmanager

from fastapi import FastAPI


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
