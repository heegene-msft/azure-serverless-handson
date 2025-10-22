#!/bin/bash
# E2E 테스트 실행 스크립트

set -e

echo "🧪 Running E2E tests..."

# 가상환경 활성화
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

# E2E 테스트 실행
python -m src.tests.test_e2e

echo "✅ E2E tests completed!"
