"""환경변수 디버깅 스크립트"""
from dotenv import load_dotenv
import os

# .env 파일 로드
load_dotenv()

print("=== 환경변수 디버깅 ===\n")

# 주요 환경변수 확인
eventhub_conn = os.getenv("EVENTHUB_CONNECTION_STRING")
eventhub_name = os.getenv("EVENTHUB_NAME")

print(f"EVENTHUB_NAME: '{eventhub_name}'")
print(f"Length: {len(eventhub_name) if eventhub_name else 0}")
print()

if eventhub_conn:
    print(f"EVENTHUB_CONNECTION_STRING exists: Yes")
    print(f"Length: {len(eventhub_conn)}")
    print(f"First 100 chars: {eventhub_conn[:100]}")
    print()
    
    # Connection String 파싱
    parts = eventhub_conn.split(';')
    print("Connection String parts:")
    for i, part in enumerate(parts):
        if 'SharedAccessKey' in part:
            print(f"  {i+1}. SharedAccessKey=***REDACTED***")
        else:
            print(f"  {i+1}. {part}")
    print()
    
    # 필수 컴포넌트 체크
    has_endpoint = any('Endpoint=' in p for p in parts)
    has_keyname = any('SharedAccessKeyName=' in p for p in parts)
    has_key = any('SharedAccessKey=' in p for p in parts)
    
    print("Required components:")
    print(f"  ✓ Endpoint: {'Yes' if has_endpoint else 'NO - MISSING!'}")
    print(f"  ✓ SharedAccessKeyName: {'Yes' if has_keyname else 'NO - MISSING!'}")
    print(f"  ✓ SharedAccessKey: {'Yes' if has_key else 'NO - MISSING!'}")
else:
    print("❌ EVENTHUB_CONNECTION_STRING not found!")

print("\n=== All environment variables starting with EVENTHUB or AZURE ===")
for key, value in os.environ.items():
    if key.startswith(('EVENTHUB', 'AZURE', 'COSMOS')):
        if 'KEY' in key or 'SECRET' in key or 'CONNECTION' in key:
            print(f"{key}: {value[:50]}... (length: {len(value)})")
        else:
            print(f"{key}: {value}")
