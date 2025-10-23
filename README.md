# Azure Serverless Hands-on

Azure Serverless 아키텍처 실습 핸즈온입니다. 가상의 디바이스가 보내는 텔레메트리 정보를 이벤트 기반으로 처리하는 시나리오입니다. 
Event Hub, Azure Functions, Cosmos DB를 활용한 실시간 이벤트 처리 파이프라인을 구축합니다.

## 🏗️ 아키텍처

### 전체 데이터 플로우

```
┌─────────────────┐
│  Event Producer │  (IoT 디바이스 시뮬레이션)
│  (Python Script)│
└────────┬────────┘
         │ Azure AD Auth
         ▼
┌─────────────────┐
│   Event Hub     │  telemetry_events
│ (Stream Ingestion)
└────────┬────────┘
         │ Event Hub Trigger
         ▼
┌─────────────────┐
│ Azure Functions │  eventhub_trigger_processor
│  (Event Handler)│  • 이벤트 파싱
└────────┬────────┘  • 데이터 변환
         │ Cosmos DB Output Binding
         ▼
┌─────────────────┐
│   Cosmos DB     │  serverless_db/events
│  (NoSQL Storage)│  • 텔레메트리 저장
└────────┬────────┘  • 파티션: /deviceId
         │ Change Feed Trigger
         ▼
┌─────────────────┐
│ Azure Functions │  cosmosdb_changefeed_processor
│ (Change Handler)│  • 실시간 모니터링
└─────────────────┘  • 임계값 체크


┌─────────────────┐
│      APIM       │  API Gateway (선택사항)
│  (API Gateway)  │  • /api/health
└────────┬────────┘  • /api/process-event
         │
         ▼
┌─────────────────┐
│ Azure Functions │  http_trigger_process_event
│  (HTTP Handler) │  • REST API
└─────────────────┘  • Cosmos DB 직접 저장
```

### 주요 구성 요소

- **Event Hub**: 디바이스 텔레메트리 수집 (초당 수천 개 이벤트)
- **Azure Functions**: 서버리스 이벤트 처리 (Python 3.11, v2 모델)
- **Cosmos DB**: 분산 NoSQL 데이터베이스 (Change Feed 지원)
- **APIM**: API 게이트웨이 및 보안 레이어
- **App Insights**: 통합 모니터링 및 로깅

## 📁 프로젝트 구조

```
azure-serverless-handson/
├── terraform/                    # OpenTofu/Terraform IaC 코드
│   ├── main.tf                  # 메인 오케스트레이션
│   ├── variables.tf             # 변수 정의
│   ├── outputs.tf               # 출력 값
│   ├── terraform.tfvars         # 변수 값 (gitignore)
│   ├── backend.tf               # Remote state 설정
│   ├── modules/                 # Infrastructure 모듈
│   │   ├── resource_group/      # 리소스 그룹
│   │   ├── storage/             # Storage Account
│   │   ├── eventhub/            # Event Hub
│   │   ├── cosmosdb/            # Cosmos DB
│   │   ├── function_app/        # Azure Functions
│   │   ├── apim/                # API Management
│   │   └── insights/            # Application Insights
│   └── README.md                # Infrastructure 가이드
│
├── src/                         # Python 소스 코드
│   ├── config/                  # Azure 설정
│   │   └── azure_config.py     # 클라이언트 팩토리
│   ├── producer/                # Event Producer
│   │   └── event_producer.py   # Event Hub 전송
│   ├── functions/               # Azure Functions
│   │   ├── function_app.py     # All functions (Python v2 model)
│   │   ├── host.json           # Function 설정
│   │   └── local.settings.json # 로컬 설정
│   └── utils/                   # 유틸리티
│       └── helpers.py           # 헬퍼 함수
│
├── scripts/                     # 실행 스크립트
│   └── send_events.sh          # 이벤트 전송
│
├── .env.template                # 환경변수 템플릿
├── requirements.txt             # Python 의존성
└── README.md                    # 이 파일
```

## 🚀 빠른 시작 (Quick Start)

### 사전 요구사항

| 도구 | 버전 | 용도 |
|------|------|------|
| **Azure CLI** | v2.50+ | Azure 인증 및 리소스 관리 |
| **OpenTofu** | v1.6+ | 인프라 배포 (Terraform 호환) |
| **Python** | v3.11 | Event Producer 실행 |
| **Azure 구독** | 🫶💖💖 | 리소스 프로비저닝 |

### 1단계: 환경 설정

혹시 opentofu/terraform 설치가 안 되어있다면:
https://opentofu.org/docs/intro/install/


```bash
# 리포지토리 클론
git clone https://github.com/heegene-msft/azure-serverless-handson.git
cd azure-serverless-handson

# Python 가상환경 생성 (선택사항)
python3.11 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt
```

### 2단계: 인프라 배포 (요걸로 인프라 및 Azure Functions 배포가 완료됩니다.)

```bash
cd terraform

# Azure 로그인
az login

# 인프라 배포 (초기화 + 배포 자동 실행)
tofu init
tofu apply -auto-approve
```

**배포 내용**:
- ✅ Event Hub (telemetry_events, device_events)
- ✅ Cosmos DB (serverless_db: devices, events, leases)
- ✅ Function App (코드 자동 배포 포함!)
- ✅ APIM + Storage + App Insights

배포 시간: **약 10분**

> 💡 자세한 내용은 [terraform/README.md](terraform/README.md) 참조

### 3단계: 환경변수 설정

Event Producer 실행을 위한 `.env` 파일 생성:

```bash
# 프로젝트 루트로 이동
cd ..

# .env 파일 생성
cat > .env << EOF
EVENTHUB_NAMESPACE=serverless-handson-dev-eh.servicebus.windows.net
EVENTHUB_NAME=telemetry_events
EOF
```

**참고**: OpenTofu가 리소스 이름을 자동 생성하므로 위 값을 그대로 사용하면 됩니다.  
(project_name="serverless-handson", environment="dev" 기준)

### 4단계: 이벤트 전송 테스트

```bash
# Event Hub로 샘플 이벤트 전송 (5개)
chmod +x scripts/send_events.sh
./scripts/send_events.sh
```

**실행 결과**:
```
✅ Event Hub Namespace: serverless-handson-dev-eh.servicebus.windows.net
✅ Event Hub Name: telemetry_events
🔐 Using Azure AD authentication (DefaultAzureCredential)
Sending 5 events to Event Hub...
✅ Successfully sent 5 events
```

### 5단계: 처리 결과 확인

#### 방법 1: Azure Portal에서 확인

1. **Function App 로그**:
   ```
   Azure Portal → Function App (serverless-handson-dev-func) 
   → Functions → eventhub_trigger_processor → Monitor
   ```
   - "EventHub trigger function processing 5 events" 메시지 확인

2. **Cosmos DB 데이터**:
   ```
   Azure Portal → Cosmos DB (serverless-handson-dev-cosmos)
   → Data Explorer → events 컨테이너
   ```
   - 5개 문서가 저장된 것 확인

3. **Change Feed 처리**:
   ```
   Function App → cosmosdb_changefeed_processor → Monitor
   ```
   - "Cosmos DB Change Feed triggered with 5 document(s)" 확인

#### 방법 2: CLI로 확인

```bash
# Function 실행 목록 확인
az functionapp function list \
  --name serverless-handson-dev-func \
  --resource-group serverless-handson-dev-rg \
  -o table

# Cosmos DB 문서 개수 확인
az cosmosdb sql container show \
  --account-name serverless-handson-dev-cosmos \
  --resource-group serverless-handson-dev-rg \
  --database-name serverless_db \
  --name events \
  --query "resource.statistics.documentCount"
```

## 모니터링 및 디버깅

### Application Insights 활용

```
Azure Portal → Application Insights (serverless-handson-dev-insights)
```

**주요 메뉴**:
- **Live Metrics**: 실시간 요청/응답/실패율
- **Transaction Search**: 개별 요청 추적 (End-to-End)
- **Failures**: 에러 분석 및 스택 트레이스
- **Performance**: 함수별 실행 시간 분석

### Cosmos DB 쿼리 예제

Azure Portal Data Explorer에서:

```sql
-- 최근 10개 이벤트 조회
SELECT TOP 10 * FROM c 
ORDER BY c.timestamp DESC

-- 특정 디바이스의 이벤트
SELECT * FROM c 
WHERE c.deviceId = 'device-001'
ORDER BY c.timestamp DESC

-- 온도 임계값 초과 이벤트
SELECT * FROM c 
WHERE c.data.temperature > 40
ORDER BY c.timestamp DESC

-- 디바이스별 이벤트 개수
SELECT c.deviceId, COUNT(1) as count
FROM c
GROUP BY c.deviceId
```

## 💡 주요 기능 설명

### 1. Event Hub Trigger (실시간 스트림 처리)

**파일**: `src/functions/function_app.py` - `eventhub_trigger_processor`

```python
@app.event_hub_message_trigger(
    arg_name="events",
    event_hub_name="telemetry_events",
    connection="EventHubConnection"
)
@app.cosmos_db_output(
    arg_name="outputDocuments",
    database_name="serverless_db",
    container_name="events",
    connection="CosmosDBConnection"
)
def eventhub_trigger_processor(events, outputDocuments):
    # 1. Event Hub에서 이벤트 수신
    # 2. 데이터 파싱 및 변환
    # 3. Cosmos DB에 자동 저장 (Output Binding)
```



### 2. Cosmos DB Change Feed (변경 감지)

**파일**: `src/functions/function_app.py` - `cosmosdb_changefeed_processor`

```python
@app.cosmos_db_trigger(
    arg_name="documents",
    database_name="serverless_db",
    container_name="events",
    connection="CosmosDBConnection",
    lease_container_name="leases"
)
def cosmosdb_changefeed_processor(documents):
    # 1. Cosmos DB 변경사항 실시간 감지
    # 2. 임계값 체크 (온도 > 40도)
    # 3. 알림/로깅 (이 핸즈온에서 다루진 않겠지만, AI Search로 탑재한다든가 하는 연동 가능)
```

**특징**:
- 실시간 변경 감지 (1초 이내)
- 재시작 시에도 위치 유지 (leases)
- 2차 처리 파이프라인 구축 가능

### 3. HTTP Trigger (REST API)

**파일**: `src/functions/function_app.py` - `http_trigger_process_event`

```python
@app.route(route="process-event", methods=["POST"])
@app.cosmos_db_output(...)
def http_trigger_process_event(req, outputDocument):
    # APIM → Function → Cosmos DB
    # REST API로 이벤트 직접 전송
```

**특징**:
- ✅ APIM을 통한 보안 API
- ✅ Subscription Key 인증
- ✅ Rate Limiting 지원

### 4. Event Producer (시뮬레이션)

**파일**: `src/producer/event_producer.py`

```python
# IoT 디바이스 시뮬레이션
event = {
    "id": "evt-12345",
    "deviceId": "device-001",
    "temperature": 25.3,
    "humidity": 60.5,
    "timestamp": "2025-10-23T10:00:00Z"
}
# Azure AD 인증으로 Event Hub에 전송
```


## 🧹 리소스 정리

```bash
cd terraform

# 모든 Azure 리소스 삭제
tofu destroy -auto-approve
```

**삭제 시간**: 약 10분


## 📄 라이선스

MIT License

---
