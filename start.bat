@echo off
REM Anki Turbo PRO - 원클릭 실행 스크립트 (Windows)

cd /d "%~dp0"

REM 가상환경 활성화 (있으면)
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
) else if exist ".venv\Scripts\activate.bat" (
    call .venv\Scripts\activate.bat
)

REM 2초 후 브라우저 열기
start "" cmd /c "timeout /t 2 /nobreak >nul && start anki_batch.html"

REM 서버 실행
echo 🚀 서버 시작 중... http://localhost:8000
python server.py
