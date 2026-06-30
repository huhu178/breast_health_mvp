#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BACKEND_DIR="$ROOT_DIR/backend"
FRONTEND_DIR="$ROOT_DIR/vue-prototype"
LOG_DIR="$ROOT_DIR/logs"

mkdir -p "$LOG_DIR"

responds() {
  local url="$1"
  local status
  status="$(curl --noproxy '*' -sS -o /dev/null -w '%{http_code}' "$url" 2>/dev/null || true)"
  [[ "$status" =~ ^(2|3)[0-9][0-9]$ ]]
}

port_busy() {
  local port="$1"
  lsof -i ":$port" >/dev/null 2>&1
}

if responds "http://127.0.0.1:5000/"; then
  echo "[OK] backend responds on :5000"
elif port_busy 5000; then
  echo "[WARN] :5000 is occupied, but backend HTTP check failed"
  echo "       Please stop the stale process or use another port."
else
  echo "[START] backend on :5000"
  (
    cd "$BACKEND_DIR"
    DISABLE_INTERNAL_VUE=1 nohup python3 -c "from app import app; app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)" > "$LOG_DIR/backend.log" 2>&1 &
    echo $! > "$LOG_DIR/backend.pid"
  )
fi

if responds "http://127.0.0.1:5173/login"; then
  echo "[OK] frontend responds on :5173"
elif port_busy 5173; then
  echo "[WARN] :5173 is occupied, but frontend HTTP check failed"
  echo "       Please stop the stale process or use another port."
else
  echo "[BUILD] frontend production assets"
  (
    cd "$FRONTEND_DIR"
    npm run build
  )
  echo "[START] frontend dev server on :5173"
  (
    cd "$FRONTEND_DIR"
    setsid -f ./node_modules/.bin/vite --host 0.0.0.0 > "$LOG_DIR/frontend.log" 2>&1
    sleep 1
    pgrep -f "$FRONTEND_DIR/node_modules/.bin/vite --host 0.0.0.0" | head -1 > "$LOG_DIR/frontend.pid"
  )
fi

echo
echo "Demo URL: http://localhost:5173/login"
echo "Account : smoke_admin / Smoke@123456"
echo
echo "Logs:"
echo "  $LOG_DIR/backend.log"
echo "  $LOG_DIR/frontend.log"
