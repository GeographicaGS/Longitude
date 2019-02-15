FROM python:3.6.6-slim

ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=0

WORKDIR /usr/src/app
ENV PATH="$PATH:/root/.poetry/bin:/usr/src/app"

ENV POETRY_VERSION 0.12.11

# Install anything missing in the slim image, install dependencies
# Remove anything only needed for building
# This is run as one line so docker caches it as a single layer.

# Install poetry
RUN \
    set -ex \
    && apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && curl -sSL https://raw.githubusercontent.com/sdispater/poetry/master/get-poetry.py | python - --version $POETRY_VERSION \
    && apt-get autoremove -y \
    && apt-get clean -y \
    && rm -rf /var/lib/apt/lists/*

# Config poetry
RUN set -x \
    && poetry config repositories.testpypi https://test.pypi.org/legacy/ \
    && poetry config settings.virtualenvs.create false

COPY pyproject.* .
COPY poetry.lock .

COPY . .

# Installing dependencies
RUN set -x \
    && apt-get update \
    && apt-get install -y --no-install-recommends git gcc \
    && poetry -vvv install \
    && apt-get remove -y --purge git gcc \
    && apt-get autoremove -y \
    && apt-get clean -y \
    && rm -rf /var/lib/apt/lists/*

# COPY . .
