#!/usr/bin/env bash
set -euo pipefail

echo "[*] Starting StockEye..."

docker compose up -d
if [ $? -ne 0 ]; then
    echo "[ERROR] Failed to start service."
    exit 1
fi

echo "[OK] StockEye is running."

echo -ne "\033]0;StockEye\007"
docker exec -it stockeye bash
