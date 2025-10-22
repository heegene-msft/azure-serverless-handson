# 빠른 시작 가이드

## 1️⃣ 초기 설정 (5분)

```bash
# 1. 가상환경 생성 및 활성화
python3.11 -m venv venv
source venv/bin/activate  # macOS/Linux
# venv\Scripts\activate   # Windows

# 2. 의존성 설치
pip install -r requirements.txt

# 3. 환경변수 파일 생성
cp .env.template .env
```

## 2️⃣ OpenTofu 인프라 배포 (15분)

```bash
cd terraform

# Azure 로그인
az login

# OpenTofu 초기화 및 배포
tofu init
tofu plan
tofu apply

# 출력 값 확인
tofu output -json > outputs.json
```

## 3️⃣ 환경변수 설정 (1분)

Event Producer 실행을 위한 `.env` 파일 생성:

```bash
cd ..  # 프로젝트 루트로

# .env 파일 생성 (Event Hub 정보만 필요)
cat > .env << EOF
EVENTHUB_NAMESPACE=serverless-handson-dev-eh.servicebus.windows.net
EVENTHUB_NAME=telemetry_events
EOF
```

> 💡 **참고**: Connection String은 필요 없습니다! Azure AD 인증을 사용합니다.

## 4️⃣ 테스트 실행 (5분)

### 이벤트 전송 테스트

```bash
cd ..  # 프로젝트 루트로
chmod +x scripts/*.sh

# Event Hub로 샘플 이벤트 전송
./scripts/send_events.sh
```



## 5️⃣ Azure Functions 로컬 실행 (선택사항)

```bash
cd src/functions

# local.settings.json 업데이트
# .env의 값들을 복사

# Functions 로컬 실행
func start

# 다른 터미널에서 테스트
curl -X POST http://localhost:7071/api/process-event \
  -H "Content-Type: application/json" \
  -d '{"id":"test-1","deviceId":"device-001","timestamp":"2024-01-01T00:00:00Z","data":{}}'
```

## 6️⃣ 모니터링

### Azure Portal에서 확인

1. **Event Hub**: 수신된 메시지 수
2. **Function App**: 실행 횟수, 성공/실패율
3. **Cosmos DB**: 저장된 문서 수
4. **Application Insights**: 전체 트랜잭션 추적

### 로컬에서 Cosmos DB 쿼리

Azure Portal의 Data Explorer를 사용하거나, Azure CLI로 확인:

```bash
# Cosmos DB 문서 개수 확인
az cosmosdb sql container show \
  --account-name serverless-handson-dev-cosmos \
  --resource-group serverless-handson-dev-rg \
  --database-name serverless_db \
  --name events \
  --query "resource.statistics"
```

또는 Azure Portal → Cosmos DB → Data Explorer에서 쿼리:
```sql
SELECT TOP 10 * FROM c ORDER BY c.timestamp DESC
```

## 7️⃣ 리소스 정리

```bash
cd terraform
tofu destroy
# 'yes' 입력하여 확인
```

## 📋 체크리스트

- [ ] Azure CLI 설치 및 로그인
- [ ] OpenTofu 설치
- [ ] Python 3.11 설치
- [ ] 가상환경 생성 및 활성화
- [ ] requirements.txt 설치
- [ ] OpenTofu 배포 완료
- [ ] .env 파일 설정
- [ ] 이벤트 전송 테스트 성공
- [ ] Azure Portal에서 리소스 확인
- [ ] Function App 로그에서 처리 확인

## 🆘 문제 해결

### Import 에러 발생

```bash
# 가상환경이 활성화되었는지 확인
which python
# 출력: /path/to/venv/bin/python

# 의존성 재설치
pip install -r requirements.txt
```

### OpenTofu 배포 실패

```bash
# Provider 캐시 정리
rm -rf terraform/.terraform
tofu init

# 특정 리소스만 재배포
tofu apply -target=module.eventhub
```

### Function이 이벤트를 받지 못함

1. Event Hub 연결 문자열 확인
2. Function App의 Application Insights 로그 확인
3. Event Hub에 실제로 메시지가 들어왔는지 확인 (Portal)

## 📚 다음 단계

1. **AI Enrichment 구현**
   - Azure AI Search 연동
   - Change Feed → AI Search 인덱싱

2. **고급 모니터링**
   - Custom metrics 추가
   - Alert rules 설정

3. **성능 최적화**
   - Cosmos DB throughput 조정
   - Function 동시성 설정

4. **보안 강화**
   - Managed Identity 사용
   - Key Vault 연동
