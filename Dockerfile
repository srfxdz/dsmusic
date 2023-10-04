FROM python:3.11 as builder

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_DEFAULT_TIMEOUT=100 \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=0 \
    POETRY_CACHE_DIR=/tmp/poetry_cache \
    PATH="$PATH:/root/.poetry/bin"

# Change workdir
WORKDIR /wheels

# Add support for armhf (raspberry)
RUN if [ "$(dpkg --print-architecture)" = "armhf" ]; \
    then export PIP_INDEX_URL="https://www.piwheels.org/simple/"; fi

# Install powrt
RUN pip install poetry==1.6.1

# Add poetry files
COPY pyproject.toml poetry.lock ./

# Use poetry to resolve dependecies
RUN poetry export -f requirements.txt --output requirements.txt
# Compile dependencies
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r requirements.txt

FROM python:3.11-slim

# Accept secrets as arguments
ARG TOKEN="discord_token"
ARG GUILD_ID="0"
ENV TOKEN $TOKEN
ENV GUILD_ID $GUILD_ID

ENV PYTHONFAULTHANDLER=1 \
      PYTHONUNBUFFERED=1 \
      PYTHONHASHSEED=random \
      PYTHONDONTWRITEBYTECODE=1 \
      # pip
      PIP_NO_CACHE_DIR=1 \
      PIP_DISABLE_PIP_VERSION_CHECK=1 \
      PIP_DEFAULT_TIMEOUT=100

# Change workdir
WORKDIR /bot

# Setting up proper permissions:
RUN groupadd -r bot && useradd -d /bot -r -g bot bot \
    && mkdir -p /bot/config && chown bot:bot -R /bot

# Run as non-root user
USER bot

# Copy wheels
COPY --from=builder /wheels /bot/wheels

# install project dependecies
RUN pip install --no-cache /wheels/*

# Copy project
COPY --chown=bot:bot dsmusic/ /bot/dsmusic/

# Commands to execute inside container
CMD ["python", "-O", "-B", "-m", "dsmusic"]
