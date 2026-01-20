#!/bin/bash
# Anki Turbo PRO - 원클릭 실행 스크립트 (macOS/Linux)

cd "$(dirname "$0")"

# 가상환경 활성화 (있으면)
if [ -d "venv" ]; then
    source venv/bin/activate
elif [ -d ".venv" ]; then
    source .venv/bin/activate
fi

# 2초 후 브라우저 열기 (백그라운드)
(sleep 2 && open "anki_batch.html" 2>/dev/null || xdg-open "anki_batch.html" 2>/dev/null) &

# 서버 실행
echo "🚀 서버 시작 중... http://localhost:8000"
python3 server.py
