FROM python:3.12-slim

LABEL maintainer="jaguar999paw-droid" \
      description="ssh-shell-mcp — AI-driven SSH orchestration MCP server"

# System deps: openssh client for key operations + build tools for asyncssh
RUN apt-get update && apt-get install -y --no-install-recommends \
    openssh-client \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Ensure logs directory exists
RUN mkdir -p logs

EXPOSE 8000

ENV SSH_HOSTS_YAML=/app/config/hosts.yaml \
    SSH_POLICIES_YAML=/app/config/policies.yaml \
    SSH_MCP_LOG_DIR=/app/logs \
    MCP_AUTH_TOKEN=""

ENTRYPOINT ["python", "server.py"]
CMD ["--transport", "streamable_http", "--port", "8000"]
