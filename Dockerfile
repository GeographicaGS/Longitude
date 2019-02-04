FROM python:3.6.6-slim

ENV PYTHONUNBUFFERED=1

WORKDIR /usr/src/app
ENV PATH="$PATH:/usr/src/app"


# Install anything missing in the slim image, install dependencies
# Remove anything only needed for building
# This is run as one line so docker caches it as a single layer.

COPY pyproject.toml .

RUN set -x \
    && apt-get update \
    && apt-get install -y --no-install-recommends git gcc curl \
    && curl -sSL https://raw.githubusercontent.com/sdispater/poetry/master/get-poetry.py | python \
    && $HOME/.poetry/bin/poetry install \
    && apt-get remove -y --purge git gcc curl \
    && apt-get autoremove -y \
    && apt-get clean -y \
    && rm -rf /var/lib/apt/lists/*

COPY . .
