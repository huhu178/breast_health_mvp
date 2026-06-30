#!/usr/bin/env bash
set -euo pipefail

check_url() {
  local name="$1"
  local url="$2"
  local status
  status="$(curl --noproxy '*' -sS -o /dev/null -w '%{http_code}' "$url" 2>/dev/null || true)"
  if [[ "$status" =~ ^(2|3)[0-9][0-9]$ ]]; then
    echo "[OK] $name responds: $url ($status)"
  else
    echo "[FAIL] $name does not respond: $url (${status:-no response})"
  fi
}

check_url "frontend login" "http://127.0.0.1:5173/login"
check_url "backend root" "http://127.0.0.1:5000/"

echo
echo "Demo URL: http://localhost:5173/login"
echo "Account : smoke_admin / Smoke@123456"
