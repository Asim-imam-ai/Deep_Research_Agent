FROM python:3.12-slim AS runtime
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
RUN pip install --no-cache-dir uv && groupadd -r app && useradd --no-log-init -r -g app app
COPY pyproject.toml README.md ./
COPY src ./src
COPY migrations ./migrations
COPY scripts ./scripts
COPY alembic.ini ./
RUN uv pip install --system --no-cache .
USER app
EXPOSE 8000
CMD ["uvicorn", "research_assistant.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
