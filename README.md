# Azure Serverless Hands-on


## 🏗️ 아키텍처

```
┌─────────────┐      ┌──────────────┐      ┌─────────────┐
│   Event     │─────▶│  Event Hub   │─────▶│   Azure     │
│  Producer   │      │              │      │  Functions  │
└─────────────┘      └──────────────┘      └─────────────┘
                                                   │
                                                   ▼
┌─────────────┐      ┌──────────────┐      ┌─────────────┐
│    APIM     │─────▶│   HTTP       │─────▶│  Cosmos DB  │
│             │      │  Trigger     │      │             │
└─────────────┘      └──────────────┘      └─────────────┘
                                                   │
                                                   ▼
                                            ┌─────────────┐
                                            │ Change Feed │
                                            │   Trigger   │
                                            └─────────────┘
                                                   │
                                                   ▼
                                            ┌─────────────┐
                                            │ AI Search   │
                                            │             │
                                            └─────────────┘
```

## 📁 프로젝트 구조

```
azure-serverless-handson/
├── terraform/                    # Terraform IaC 코드
│   ├── main.tf                  # 메인 오케스트레이션
│   ├── variables.tf             # 변수 정의
│   ├── outputs.tf               # 출력 값
│   ├── terraform.tfvars         # 변수 값 (gitignore)
│   ├── backend.tf               # Remote state 설정
│   ├── modules/                 # Terraform 모듈
│   │   ├── resource_group/      # 리소스 그룹
│   │   ├── storage/             # Storage Account
│   │   ├── eventhub/            # Event Hub
│   │   ├── cosmosdb/            # Cosmos DB
│   │   ├── function_app/        # Azure Functions
│   │   ├── apim/                # API Management
│   │   └── insights/            # Application Insights
│   └── README.md                # Terraform 사용 가이드
│
├── src/                         # Python 소스 코드
│   ├── config/                  # Azure 설정
│   │   └── azure_config.py     # 클라이언트 팩토리
│   ├── producer/                # Event Producer
│   │   └── event_producer.py   # Event Hub 전송
│   ├── functions/               # Azure Functions
│   │   ├── http_trigger.py     # HTTP Trigger
│   │   ├── eventhub_trigger.py # Event Hub Trigger
│   │   ├── cosmosdb_trigger.py # Change Feed Trigger
│   │   ├── host.json           # Function 설정
│   │   └── local.settings.json # 로컬 설정
│   ├── tests/                   # 테스트 코드
│   │   ├── test_e2e.py         # E2E 통합 테스트
│   │   └── test_unit.py        # 유닛 테스트
│   └── utils/                   # 유틸리티
│       └── helpers.py           # 헬퍼 함수
│
├── scripts/                     # 실행 스크립트
│   ├── send_events.sh          # 이벤트 전송
│   ├── run_e2e_tests.sh        # E2E 테스트
│   └── run_unit_tests.sh       # 유닛 테스트
│
├── .env.template                # 환경변수 템플릿
├── requirements.txt             # Python 의존성
└── README.md                    # 이 파일
```

## 셋업하기

### 환경 요구사항

- **Azure CLI** (v2.50+)
- **Terraform** (v1.0+)
- **Python** (v3.11)
- **Azure Functions Core Tools** (v4.x)
- Azure 구독(♥️🫶♥️)

### 1. 환경 설정

```bash
# 리포지토리 클론
git clone <repository-url>
cd azure-serverless-handson

# Python 가상환경 생성 (꼭 venv 쓰실 필욘 없습니다 :) 편하신대로!)
python3.11 -m venv venv
source venv/bin/activate  

# 의존성 설치
pip install -r requirements.txt

# 환경변수 설정
cp .env.template .env
# .env 파일을 편집하여 실제 값으로 채우기
```

### 2. Terraform 인프라 배포

```bash
cd terraform

# Azure 로그인
az login

# Terraform 초기화
terraform init

# 배포 계획 확인
terraform plan

# 인프라 배포
terraform apply

# 출력 값 확인 (연결 문자열 등)
terraform output
```

자세한 내용은 [terraform/README.md](terraform/README.md) 참조

### 3. 환경변수 설정

Terraform 출력 값을 사용하여 `.env` 파일 업데이트:

```bash
# Terraform 출력에서 값 복사
terraform output eventhub_connection_string
terraform output cosmos_connection_string

# .env 파일에 붙여넣기
```

### 4. Azure Functions 로컬 실행 (선택사항)

```bash
cd src/functions

# local.settings.json 업데이트
# .env의 값을 local.settings.json에 복사

# Functions 로컬 실행
func start
```

## 🧪 테스트

### 이벤트 전송

```bash
# Event Hub로 테스트 이벤트 전송
chmod +x scripts/send_events.sh
./scripts/send_events.sh
```

### 유닛 테스트

```bash
chmod +x scripts/run_unit_tests.sh
./scripts/run_unit_tests.sh
```

### E2E 통합 테스트

```bash
chmod +x scripts/run_e2e_tests.sh
./scripts/run_e2e_tests.sh
```

## 모니터링

### Application Insights

Azure Portal에서 Application Insights 확인:
- Live Metrics: 실시간 요청/응답
- Transaction Search: 개별 트랜잭션 추적
- Failures: 오류 분석
- Performance: 성능 메트릭

### Cosmos DB 쿼리

```bash
# Azure Portal Data Explorer에서 쿼리
SELECT * FROM c WHERE c.eventType = 'telemetry'
ORDER BY c.timestamp DESC
```

## 함수 개발 가이드

### Azure Functions 개발

1. **HTTP Trigger 예제** (`src/functions/http_trigger.py`)
   - APIM → Function → Cosmos DB
   - RESTful API 엔드포인트

2. **Event Hub Trigger 예제** (`src/functions/eventhub_trigger.py`)
   - Event Hub → Function → Cosmos DB
   - 실시간 스트림 처리

3. **Cosmos DB Change Feed Trigger 예제** (`src/functions/cosmosdb_trigger.py`)
   - Cosmos DB → Function
   - 변경 감지 및 후속 처리

### Event Producer 사용

```python
from src.config import AzureConfig, AzureClientFactory
from src.producer import EventProducer

# 설정 로드
config = AzureConfig.from_env()
AzureClientFactory.initialize(config)

# Producer 생성
producer_client = AzureClientFactory.get_eventhub_producer()
event_producer = EventProducer(producer_client)

# 이벤트 생성 및 전송
event = event_producer.create_sample_event("device-001")
event_producer.send_single_event(event)
```

## 🛠️ 문제 해결

### Function이 Event Hub 메시지를 받지 못할 때

1. `EventHubConnection` 연결 문자열 확인
2. Event Hub 권한 확인 (Listen)
3. Function App의 Application Insights 로그 확인

### Cosmos DB 연결 오류

1. `CosmosDBConnection` 연결 문자열 확인
2. 방화벽 규칙 확인 (Azure Portal)
3. RBAC 권한 확인 (Data Contributor)

### Terraform 배포 실패

1. Azure 구독 활성화 확인
2. 리소스 이름 중복 확인
3. 리전 할당량 확인

## 📚 참고 자료

- [Azure Event Hubs Documentation](https://learn.microsoft.com/azure/event-hubs/)
- [Azure Functions Python Developer Guide](https://learn.microsoft.com/azure/azure-functions/functions-reference-python)
- [Azure Cosmos DB Documentation](https://learn.microsoft.com/azure/cosmos-db/)
- [Terraform Azure Provider](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs)


## 🧹 리소스 정리

```bash
cd terraform

# 모든 리소스 삭제
terraform destroy

# 확인 메시지에 'yes' 입력
```

## 라이선스

MIT License

