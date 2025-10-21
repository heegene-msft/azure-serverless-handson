#!/bin/bash
# 이벤트 전송 스크립트

set -e

echo "🚀 Sending test events to Event Hub..."

# 가상환경 활성화 (존재하는 경우)
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# 환경변수 로드
if [ -f ".env" ]; then
    export $(cat .env | grep -v '^#' | xargs)
else
    echo "⚠️  .env file not found. Please create one from .env.template"
    exit 1
fi

# Event Producer 실행
python -m src.producer.event_producer

echo "✅ Events sent successfully!"
