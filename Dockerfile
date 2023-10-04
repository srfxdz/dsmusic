FROM python:bullseye

ARG TOKEN="discord_token"
ARG GUILD_ID="0"
ENV TOKEN $TOKEN
ENV GUILD_ID $GUILD_ID

ENV PYTHONFAULTHANDLER=1 \
      PYTHONUNBUFFERED=1 \
      PYTHONHASHSEED=random \
      PYTHONDONTWRITEBYTECODE=1 \
      # pip
      PIP_NO_CACHE_DIR=off \
      PIP_DISABLE_PIP_VERSION_CHECK=on \
      PIP_DEFAULT_TIMEOUT=100 \
      # poetry
      POETRY_NO_INTERACTION=1 \
      POETRY_VIRTUALENVS_CREATE=false \
      POETRY_CACHE_DIR="/var/cache/pypoetry" \
      PATH="$PATH:/root/.poetry/bin"

# System deps
RUN if [ "$(dpkg --print-architecture)" = "armhf" ] || [ "$(dpkg --print-architecture)" = "arm64" ]; \
    then export PIP_INDEX_URL="https://www.piwheels.org/simple/"; fi

# Setting up proper permissions:
RUN groupadd -r bot && useradd -d /bot -r -g bot bot \
    && mkdir -p /bot && chown bot:bot -R /bot

# Change workdir
WORKDIR /bot

# install project dependecies
RUN python -m pip install --upgrade pip \
    && pip install discord.py mafic uvloop

# Copy project
COPY --chown=bot:bot . /bot

# run as non-root user
USER bot

# Commands to execute inside container
CMD ["python", "-O", "-B", "-m", "dsmusic"]