FROM python:3.12-bookworm as builder

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_DEFAULT_TIMEOUT=100 \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=0 \
    POETRY_CACHE_DIR=/tmp/poetry_cache \
    PATH="$PATH:/root/.poetry/bin"

# Change workdir
WORKDIR /build

# Install powrt
RUN pip install poetry

# Add poetry files
COPY pyproject.toml poetry.lock ./

# Use poetry to resolve dependecies
RUN mkdir -p /build/wheels && poetry export -f requirements.txt --output /build/wheels/requirements.txt
# Compile dependencies
WORKDIR /build/wheels
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /build/wheels -r /build/wheels/requirements.txt

FROM python:3.12-slim-bookworm

ENV PYTHONFAULTHANDLER=1 \
      PYTHONUNBUFFERED=1 \
      PYTHONHASHSEED=random \
      PYTHONDONTWRITEBYTECODE=1 \
      # pip
      PIP_NO_CACHE_DIR=1 \
      PIP_DISABLE_PIP_VERSION_CHECK=1 \
      PIP_DEFAULT_TIMEOUT=100

ENV DS_TOKEN     "YOUR_DISCORD_TOKEN"     # discord token from the developer portal
ENV DS_GUILD_ID  "YOUR_GUILD_ID"          # the guild id where the bot will be used
ENV CF_CLIENT_ID "YOUR_CLIENT_ID"         # cloudflare client id
ENV CF_TOKEN     "YOUR_CLOUDFLARE_TOKEN"  # cloudflare token

# Change workdir
WORKDIR /bot

# Setting up proper permissions:
RUN groupadd -r bot && useradd -d /bot -r -g bot bot \
    && mkdir -p /bot/config && chown bot:bot -R /bot

# Run as non-root user
USER bot

# Copy wheels
COPY --from=builder /build/wheels /bot/wheels

# install project dependecies
RUN pip install --find-links /bot/wheels -r /bot/wheels/requirements.txt

# Copy project
COPY --chown=bot:bot dsmusic/ /bot/dsmusic/

VOLUME ["/bot/config"]
VOLUME ["/bot/data"]

# Commands to execute inside container
CMD ["python", "-O", "-B", "-m", "dsmusic"]
