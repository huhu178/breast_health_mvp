#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LOG_DIR="$ROOT_DIR/logs"

stop_pid_file() {
  local name="$1"
  local file="$2"
  if [[ -f "$file" ]]; then
    local pid
    pid="$(cat "$file")"
    if [[ -n "$pid" ]] && kill -0 "$pid" >/dev/null 2>&1; then
      echo "[STOP] $name pid=$pid"
      kill "$pid"
    else
      echo "[SKIP] $name pid file exists but process is not running"
    fi
    rm -f "$file"
  else
    echo "[SKIP] no pid file for $name"
  fi
}

stop_port() {
  local name="$1"
  local port="$2"
  local pids
  pids="$(lsof -ti ":$port" 2>/dev/null || true)"
  if [[ -n "$pids" ]]; then
    echo "[STOP] $name port=:$port pids=$(echo "$pids" | tr '\n' ' ')"
    kill $pids
  else
    echo "[SKIP] no process listening on :$port"
  fi
}

stop_pid_file "frontend" "$LOG_DIR/frontend.pid"
stop_pid_file "backend" "$LOG_DIR/backend.pid"

stop_port "frontend" 5173
stop_port "backend" 5000
