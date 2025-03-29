FROM python:3.11-slim-buster

# Install poetry
RUN pip install poetry==1.4.2

ENV POETRY_NO_INTERACTION=1 \
  POETRY_VIRTUALENVS_IN_PROJECT=1 \
  POETRY_VIRTUALENVS_CREATE=1 \
  POETRY_CACHE_DIR=/tmp/poetry_cache \
  PATH="/app/.venv/bin:$PATH"

WORKDIR /app

# Install the dependencies
COPY pyproject.toml poetry.lock ./
RUN poetry install --without dev --no-root && rm -rf $POETRY_CACHE_DIR

# Run the spider to generate the lotspy.db file
COPY lotspy lotspy
COPY scrapy.cfg scrapy.cfg

RUN scrapy crawl parcels -o lotspy.db \
  && scrapy crawl noorp -o lotspy.db \
  && rm -rf .scrapy

# Copy the datasette app
COPY datasette datasette

# Move our database file to the datasette folder
RUN mv lotspy.db datasette/

ENV PORT=8000
EXPOSE $PORT

# Run the datasette server
# --cors allows frontend access from across domains
# -i opens the file in immutable mode
ENTRYPOINT datasette ./datasette -h 0.0.0.0 -p $PORT
