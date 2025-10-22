# Azure Serverless Hands-on

IoT 텔레메트리 데이터 처리를 위한 Azure Serverless 아키텍처 실습 프로젝트입니다.  
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
| **Azure 구독** | Active | 리소스 프로비저닝 |

### 1단계: 환경 설정

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

### 2단계: 인프라 배포 (One Command!)

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
- ✅ Managed Identity 기반 인증 (Connection String 불필요)

배포 시간: **약 5-10분**

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

## 📊 모니터링 및 디버깅

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

**특징**:
- ✅ 초당 수천 개 이벤트 처리
- ✅ 배치 처리 지원 (cardinality="many")
- ✅ Managed Identity 인증

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
    # 3. 알림/로깅 (실제로는 다른 시스템 연동 가능)
```

**특징**:
- ✅ 실시간 변경 감지 (1초 이내)
- ✅ 재시작 시에도 위치 유지 (leases)
- ✅ 2차 처리 파이프라인 구축 가능

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

**특징**:
- ✅ Connection String 불필요 (Azure AD)
- ✅ 배치 전송 지원
- ✅ 샘플 데이터 자동 생성

## 🛠️ 문제 해결 (Troubleshooting)

### ❌ "No HTTP triggers found" 에러

**원인**: Python v2 모델에서 여러 개의 `FunctionApp()` 인스턴스 생성  
**해결**: `function_app.py`에 단일 `app` 인스턴스만 사용

### ❌ Event Hub 이벤트를 Function이 받지 못함

**확인 사항**:
```bash
# 1. Function App 설정 확인
az functionapp config appsettings list \
  --name serverless-handson-dev-func \
  --resource-group serverless-handson-dev-rg \
  | grep EventHub

# 2. Event Hub에 실제로 메시지가 들어왔는지 확인
az eventhubs eventhub show \
  --resource-group serverless-handson-dev-rg \
  --namespace-name serverless-handson-dev-eh \
  --name telemetry_events
```

**해결**:
- Function App의 `EventHubConnection__fullyQualifiedNamespace` 설정 확인
- Managed Identity에 "Azure Event Hubs Data Receiver" 역할 할당 확인

### ❌ Cosmos DB 권한 오류 (403 Forbidden)

**원인**: Managed Identity에 데이터 플레인 권한 없음  
**해결**:
```bash
# Cosmos DB Built-in Data Contributor 역할 확인
az cosmosdb sql role assignment list \
  --account-name serverless-handson-dev-cosmos \
  --resource-group serverless-handson-dev-rg
```

### ❌ Change Feed가 "leases 컨테이너 없음" 에러

**원인**: `leases` 컨테이너가 생성되지 않음  
**해결**: `tofu apply`로 재배포하여 leases 컨테이너 생성

### ❌ OpenTofu 배포 실패

**일반적인 원인**:
1. Azure CLI 인증 만료 → `az login` 재실행
2. 구독 할당량 초과 → Portal에서 할당량 확인
3. 리소스 이름 중복 → `terraform.tfvars`에서 `project_name` 변경

```bash
# Provider 캐시 정리 후 재시도
rm -rf terraform/.terraform
cd terraform && tofu init && tofu apply
```

## 🎓 학습 포인트

### 이 프로젝트에서 배울 수 있는 것:

1. **Infrastructure as Code (IaC)**
   - OpenTofu로 Azure 리소스 자동 배포
   - 모듈화된 인프라 설계
   - State 관리 및 의존성 관리

2. **Serverless 아키텍처**
   - Event-driven 패턴 구현
   - Azure Functions 트리거 종류별 활용
   - Auto-scaling 및 비용 최적화

3. **보안 Best Practices**
   - Managed Identity로 Connection String 제거
   - RBAC 기반 세밀한 권한 관리
   - APIM을 통한 API 보안 계층

4. **실시간 데이터 처리**
   - Event Hub로 고성능 스트림 수집
   - Cosmos DB Change Feed로 변경 감지
   - 멀티스테이지 파이프라인 구축

5. **Python v2 Programming Model**
   - 데코레이터 기반 함수 정의
   - Input/Output Bindings 활용
   - 단일 파일 배포 구조

## 🧹 리소스 정리

**⚠️ 주의**: 모든 데이터가 영구 삭제됩니다!

```bash
cd terraform

# 모든 Azure 리소스 삭제
tofu destroy -auto-approve
```

**삭제 시간**: 약 5-10분

## 📚 참고 자료

### Azure 공식 문서
- [Azure Event Hubs](https://learn.microsoft.com/azure/event-hubs/)
- [Azure Functions Python Guide](https://learn.microsoft.com/azure/azure-functions/functions-reference-python)
- [Azure Functions Python v2 Model](https://learn.microsoft.com/azure/azure-functions/functions-reference-python?tabs=asgi%2Capplication-level)
- [Cosmos DB Change Feed](https://learn.microsoft.com/azure/cosmos-db/change-feed)
- [Managed Identity](https://learn.microsoft.com/azure/active-directory/managed-identities-azure-resources/overview)

### Infrastructure as Code
- [OpenTofu Documentation](https://opentofu.org/docs/)
- [Azure Provider](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs)

### 관련 GitHub 리포지토리
- [Azure Functions Samples](https://github.com/Azure/azure-functions-python-samples)
- [Azure Serverless Community Library](https://serverlesslibrary.net/)

## 🤝 기여 (Contributing)

Issue 및 Pull Request 환영합니다!

### 개선 아이디어
- [ ] Azure Service Bus 통합
- [ ] Azure AI Search 인덱싱
- [ ] Grafana 대시보드
- [ ] GitHub Actions CI/CD
- [ ] Azure Container Apps 마이그레이션

## 📄 라이선스

MIT License

---

**만든이**: [@heegene-msft](https://github.com/heegene-msft)  
**프로젝트**: Azure Serverless Hands-on Workshop

