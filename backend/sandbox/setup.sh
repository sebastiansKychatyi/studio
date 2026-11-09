#!/bin/sh
# Sandbox of one panel user for the regular chats (ASSISTANT_SANDBOX=docker):
#   A) own Linux user claude-<name> that owns only <ASSISTANT_CLAUDE_HOME>/<name>
#   B) own container claude-<name> running as that user, with only that folder mounted
# The panel backend, its .env and the database are not visible inside.
#
# Usage (as root):  ASSISTANT_CLAUDE_HOME=/srv/claude sh backend/sandbox/setup.sh seb [--rebuild]
set -eu

name="${1:?usage: setup.sh <panel username> [--rebuild]}"
name=$(echo "$name" | tr '[:upper:]' '[:lower:]')
root="${ASSISTANT_CLAUDE_HOME:-/srv/claude}"
image="${SANDBOX_IMAGE:-claude-sandbox}"
box="${ASSISTANT_SANDBOX_PREFIX:-claude-}$name"
here=$(cd "$(dirname "$0")" && pwd)

# A) Linux user without a login shell
id "$box" >/dev/null 2>&1 || useradd --system --no-create-home --shell /usr/sbin/nologin "$box"
uid=$(id -u "$box")
gid=$(id -g "$box")
mkdir -p "$root/$name/work"
chown -R "$uid:$gid" "$root/$name"
chmod 700 "$root/$name"

# B) Image (once, or again with --rebuild for a newer Claude Code) and the container
if [ "${2:-}" = "--rebuild" ] || ! docker image inspect "$image" >/dev/null 2>&1; then
  docker build --pull -t "$image" "$here"
fi
docker rm -f "$box" >/dev/null 2>&1 || true
docker run -d --name "$box" --restart unless-stopped \
  --user "$uid:$gid" --cap-drop ALL --security-opt no-new-privileges \
  --pids-limit 512 --memory 2g --cpus 2 \
  -e HOME=/home/claude -v "$root/$name:/home/claude" \
  "$image" >/dev/null

echo "Container $box is running."
echo "Log in with your own Claude subscription (once):  docker exec -it $box claude   → /login, then /exit"
