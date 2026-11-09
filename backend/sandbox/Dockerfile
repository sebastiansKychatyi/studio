# Sandbox for the panel's regular chats: Claude Code CLI with a shell, files and Node / Python.
# One container per panel user (see setup.sh); the workspace and the login live in the mounted /home/claude.
FROM node:22-bookworm-slim

RUN apt-get update \
 && apt-get install -y --no-install-recommends git python3 python3-venv curl ca-certificates ripgrep \
 && rm -rf /var/lib/apt/lists/*
RUN npm install -g @anthropic-ai/claude-code && npm cache clean --force

# Updates come with a new image (setup.sh --rebuild), not inside a running container
ENV DISABLE_AUTOUPDATER=1 HOME=/home/claude
WORKDIR /home/claude/work
CMD ["sleep", "infinity"]
