#!/bin/bash
# 마음 필사(筆寫) 웹 애플리케이션 실행 스크립트

APP_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$APP_DIR"

PORT=8080

echo "=================================================="
echo " 🖋️ 마음 필사(筆寫) - Gemini AI 필사 노트 앱"
echo "=================================================="
echo "서버를 실행합니다: http://localhost:$PORT"
echo "종료하려면 터미널에서 Ctrl + C 를 누르세요."
echo "=================================================="

# 1초 후 기본 브라우저 자동 오픈
(sleep 1 && open "http://localhost:$PORT") &

python3 "$APP_DIR/app.py" $PORT
