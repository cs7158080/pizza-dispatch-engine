FROM python:3.12-slim AS runtime

ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1

RUN adduser --system --group app && mkdir -p /app && chown app:app /app
WORKDIR /app

# Dependencies before source: editing code must not reinstall them.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# The package itself; its dependencies are already installed and pinned above.
# `build` is removed: it is a duplicate copy of the source that nothing imports.
COPY pyproject.toml .
COPY src/ ./src/
RUN pip install --no-cache-dir --no-deps . && rm -rf build

USER app
CMD ["uvicorn", "pizza.entrypoints.api.main:app", "--host", "0.0.0.0", "--port", "8000"]


FROM runtime AS test

USER root
COPY requirements-dev.txt .
RUN pip install --no-cache-dir -r requirements-dev.txt
COPY --chown=app:app tests/ ./tests/
USER app
