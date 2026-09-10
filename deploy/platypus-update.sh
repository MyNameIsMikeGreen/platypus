#!/usr/bin/env bash
# Checks origin/main for new commits and redeploys Platypus if it has moved on.
# Intended to be run periodically by platypus-update.timer (see deploy/README.md).
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
LOCK_FILE="/tmp/platypus-update.lock"
BRANCH="main"

# Prevent overlapping runs if a previous check/build is still in progress
# (e.g. a slow build outlasting the timer interval).
exec 9>"${LOCK_FILE}"
if ! flock -n 9; then
    echo "Update already in progress, skipping this run."
    exit 0
fi

cd "${REPO_DIR}"

# Respect a deliberate `docker compose down`: only redeploy if the app
# container is currently running. This avoids the timer bringing Platypus
# back up when it was intentionally stopped (e.g. for maintenance).
container_id="$(docker compose ps -aq app 2>/dev/null || true)"
is_running="false"
if [[ -n "${container_id}" ]]; then
    is_running="$(docker inspect -f '{{.State.Running}}' "${container_id}" 2>/dev/null || echo false)"
fi

if [[ "${is_running}" != "true" ]]; then
    echo "Platypus is not currently running; skipping auto-update so a deliberate shutdown is respected."
    exit 0
fi

git fetch --quiet origin "${BRANCH}"

local_sha="$(git rev-parse HEAD)"
remote_sha="$(git rev-parse "origin/${BRANCH}")"

if [[ "${local_sha}" == "${remote_sha}" ]]; then
    echo "Platypus is already up to date (${local_sha})."
    exit 0
fi

echo "Update available: ${local_sha} -> ${remote_sha}. Deploying..."

# Fast-forward only: fail loudly rather than silently merge/rebase if the
# local checkout has diverged from origin/main.
git pull --ff-only origin "${BRANCH}"

# `docker compose up --build -d` builds the new image first and only swaps
# the running container once the new image is ready, keeping downtime to a
# brief container restart rather than a full `down` + rebuild window.
docker compose up --build -d

echo "Deployed $(git rev-parse HEAD)."
