#!/bin/bash
# Safe production deploy for AI Pathway (Hetzner).
#
# Encodes the deploy flow validated during the Jun 2026 deploys, with the guard
# that was missing when PR #28's undeclared PyJWT dependency took prod down:
#   - resets /opt/ai-pathway to origin/main (preserving the prod backend/.env,
#     which is untracked, so it is NOT overwritten - unlike deploy-hetzner.sh)
#   - builds the images
#   - IMPORT SMOKE on the freshly built backend image BEFORE swapping containers:
#     `python -c "import app.main"`. If the built image can't import the app
#     (e.g. an undeclared dependency), the deploy ABORTS and the running
#     containers are left untouched. This is the line of defense that turns a
#     prod outage into a failed deploy.
#   - only on success: `docker compose up -d`
#   - post-deploy health check
#
# Usage (from your laptop):  bash scripts/deploy-prod.sh
set -euo pipefail

SERVER="root@95.216.199.47"
APP_DIR="/opt/ai-pathway"

echo "[1/5] reset $APP_DIR to origin/main (preserving untracked .env)"
ssh -o ConnectTimeout=15 "$SERVER" "cd $APP_DIR && git fetch origin -q && git reset --hard origin/main && git log --oneline -1"

echo "[2/5] build images"
ssh "$SERVER" "cd $APP_DIR && docker compose build"

echo "[3/5] IMPORT SMOKE on the built backend image (abort deploy on failure)"
if ! ssh "$SERVER" "cd $APP_DIR && docker compose run --rm --no-deps backend python -c 'import app.main; print(\"import OK\")'"; then
  echo "[ABORT] built backend image failed to import app.main - NOT swapping containers."
  echo "        The currently running deployment is untouched. Fix the build, then retry."
  exit 1
fi

echo "[4/5] bring up new containers"
ssh "$SERVER" "cd $APP_DIR && docker compose up -d"

echo "[5/5] health check"
ssh "$SERVER" "cd $APP_DIR && sleep 3 && curl -sf http://localhost:3000/api/auth/status >/dev/null && echo 'health OK' || echo 'WARN: health check did not pass - check logs'"

echo "Done. Remember the post-deploy gates: sweep_integrity.py (Gate 1) + verify_profile_e2e.py (Gate 2)."
