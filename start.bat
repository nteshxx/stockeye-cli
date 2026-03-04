@echo off
setlocal enabledelayedexpansion

echo [*] Starting StockEye...

docker compose up -d
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Failed to start service.
    exit /b %ERRORLEVEL%
)

echo [OK] StockEye is running.
start "StockEye" cmd.exe /k "title StockEye && docker exec -it stockeye bash"
endlocal
