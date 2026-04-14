FROM python:3.11-slim

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

# Install dependencies first (layer-cached)
COPY pyproject.toml .
RUN uv sync --no-dev --no-install-project

# Copy source
COPY src/ src/
COPY langgraph.json .

# Install the project itself
RUN uv sync --no-dev

EXPOSE 2024

# Runtime env vars (set when running the container):
#   OPENROUTER_API_KEY  — your OpenRouter API key
#   OPENROUTER_MODEL    — e.g. openai/gpt-4o-mini

CMD ["uv", "run", "langgraph", "dev", "--host", "0.0.0.0", "--port", "2024", "--no-browser"]
