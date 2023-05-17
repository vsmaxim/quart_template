# Dockerfile
FROM nginx/unit:1.29.1-python3.11 as builder

# Variables for build
ENV PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \ PIP_DEFAULT_TIMEOUT=100 \
    POETRY_VERSION=1.3.2 \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=true \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_CACHE_DIR='/var/cache/pypoetry' \
    POETRY_HOME='/usr/local'

RUN export PATH="$PATH:/var/local/bin"

# Install libraries & package manager
RUN set -ex && \
    apt-get update && \
    apt-get install --no-install-recommends -y curl && \
    # Installing `poetry` package manager
    # https://github.com/python-poetry/poetry
    curl -sSL 'https://install.python-poetry.org' | python - && \
    poetry --version && \
    # Cleaning cache
    apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false && \
    apt-get clean -y && rm -rf /var/lib/apt/lists/*

# Set working dir
WORKDIR /server

# Copy only requirements, to cache them in docker layer
COPY ./poetry.lock ./pyproject.toml /server/

# Install only project dependencies for caching
RUN --mount=type=cache,target="$POETRY_CACHE_DIR" \
    poetry version && \
    poetry run pip install -U pip && \
    poetry install --no-interaction --no-ansi --without dev --no-root

# Copy project files
COPY --chown=builduser:buildgroup . .

# Install project as a python package
RUN --mount=type=cache,target="${POETRY_CACHE_DIR}" \
    # No dependencies install, only root package for imports
    poetry install --only-root

# Setup base image
FROM nginx/unit:1.29.1-python3.11

# Copy installed packages and server code
COPY --from=builder --chown=unit:unit /server /server
COPY --from=builder /usr/local /usr/local

# Copy configuration to the entrypoint directory
RUN cp /server/unit-config.json /docker-entrypoint.d/unit-config.json

# Setup permissions for user
RUN chown -R unit:unit /var/lib/unit /var/run /server
