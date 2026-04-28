@echo off
echo ================================================
echo   GiftFinder.ai Backend Server
echo ================================================
echo.

cd /d "%~dp0"

echo Checking Python environment...
python --version
echo.

echo Starting FastAPI server at http://localhost:8000
echo Press Ctrl+C to stop.
echo.

uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload --log-level info

pause
