#!/bin/bash
# 유닛 테스트 실행 스크립트

set -e

echo "🧪 Running unit tests with pytest..."

# 가상환경 활성화
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# pytest 실행 (커버리지 포함)
pytest src/tests/test_unit.py -v --cov=src --cov-report=term-missing

echo "✅ Unit tests completed!"
