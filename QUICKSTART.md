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

## 2️⃣ Terraform 인프라 배포 (15분)

```bash
cd terraform

# Azure 로그인
az login

# Terraform 초기화 및 배포
terraform init
terraform plan
terraform apply

# 출력 값 확인
terraform output -json > outputs.json
```

## 3️⃣ 환경변수 설정 (5분)

Terraform 출력 값을 `.env` 파일에 복사:

```bash
# Event Hub
terraform output eventhub_connection_string
# → .env의 EVENTHUB_CONNECTION_STRING에 복사

# Cosmos DB
terraform output cosmos_connection_string
# → .env의 COSMOS_CONNECTION_STRING에 복사

# API Management
terraform output apim_gateway_url
# → .env의 APIM_GATEWAY_URL에 복사
```

## 4️⃣ 테스트 실행 (5분)

### 이벤트 전송 테스트

```bash
cd ..  # 프로젝트 루트로
chmod +x scripts/*.sh

# Event Hub로 샘플 이벤트 전송
./scripts/send_events.sh
```

### E2E 통합 테스트

```bash
# 전체 플로우 테스트 (Event → EventHub → Function → CosmosDB)
./scripts/run_e2e_tests.sh
```

### 유닛 테스트

```bash
# 개별 컴포넌트 테스트
./scripts/run_unit_tests.sh
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

```python
from azure.cosmos import CosmosClient
import os

client = CosmosClient.from_connection_string(os.getenv("COSMOS_CONNECTION_STRING"))
database = client.get_database_client("serverless-db")
container = database.get_container_client("events")

# 최근 10개 이벤트 조회
for item in container.query_items(
    query="SELECT TOP 10 * FROM c ORDER BY c.timestamp DESC",
    enable_cross_partition_query=True
):
    print(item)
```

## 7️⃣ 리소스 정리

```bash
cd terraform
terraform destroy
# 'yes' 입력하여 확인
```

## 📋 체크리스트

- [ ] Azure CLI 설치 및 로그인
- [ ] Terraform 설치
- [ ] Python 3.11 설치
- [ ] 가상환경 생성 및 활성화
- [ ] requirements.txt 설치
- [ ] Terraform 배포 완료
- [ ] .env 파일 설정
- [ ] 이벤트 전송 테스트 성공
- [ ] E2E 테스트 성공
- [ ] Azure Portal에서 리소스 확인

## 🆘 문제 해결

### Import 에러 발생

```bash
# 가상환경이 활성화되었는지 확인
which python
# 출력: /path/to/venv/bin/python

# 의존성 재설치
pip install -r requirements.txt
```

### Terraform 배포 실패

```bash
# Provider 캐시 정리
rm -rf terraform/.terraform
terraform init

# 특정 리소스만 재배포
terraform apply -target=module.eventhub
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
