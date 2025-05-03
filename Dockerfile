###############################################################################
# Stage 1 – Build                                                             #
###############################################################################
FROM python:3.11-slim AS build

ENV PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# System deps for pandas / matplotlib
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential g++ libc6-dev libjpeg-dev git \
    && rm -rf /var/lib/apt/lists/*

# Copy project metadata (pyproject.toml) and install deps
COPY pyproject.toml ./
RUN pip install --upgrade pip setuptools wheel
RUN pip install --no-cache-dir -e .                      # installs "clearly"

# Copy the application code
COPY server/  ./server/
COPY clearly/ ./clearly/

###############################################################################
# Stage 2 – Runtime                                                           #
###############################################################################
FROM python:3.11-slim

# Choose a non‑root user
RUN useradd -m appuser
WORKDIR /app
COPY --from=build /usr/local /usr/local
COPY --from=build /app/server /app/server
COPY --from=build /app/clearly /app/clearly

# Environment variables
ENV PYTHONUNBUFFERED=1 \
    PORT=8000 \
    CD_CACHE_URL=memory://            

# set to redis://… in prod if you use Redis

EXPOSE $PORT
USER appuser

# Uvicorn entrypoint
CMD ["uvicorn", "server.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
