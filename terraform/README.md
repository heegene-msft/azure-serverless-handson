# ================================================================
# Azure Serverless Handson - Infrastructure as Code
# ================================================================
# Azure에서 이벤트 기반 데이터 처리를 위한 서버리스 아키텍처를 생성합니다.
# 
# Terraform과 OpenTofu 모두 호환됩니다.

## 📋 아키텍처

```
이벤트 → Event Hub → APIM → Functions → Cosmos DB
                                    ↓
                            App Insights
```

## 🎯 생성되는 리소스

1. **Resource Group** - 모든 리소스를 담는 컨테이너
2. **Storage Account** - Function 및 데이터를 위한 Blob 스토리지
3. **Event Hub** - 이벤트 스트리밍 플랫폼
4. **Cosmos DB** - Change Feed 지원 NoSQL 데이터베이스
5. **Function App** - 서버리스 컴퓨팅 (Python 3.11)
6. **API Management** - 정책이 적용된 API 게이트웨이
7. **Application Insights** - 모니터링 및 진단

## 🚀 시작하기

### 사전 요구사항

- [OpenTofu](https://opentofu.org/docs/intro/install/) >= 1.6 (권장) **또는** [Terraform](https://www.terraform.io/downloads.html) >= 1.0
- [Azure CLI](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli)
- Azure 구독

### 배포 단계

1. **Azure 로그인**
   ```bash
   az login
   az account set --subscription "<your-subscription-id>"
   ```

2. **초기화**
   ```bash
   cd terraform
   tofu init  # Terraform 사용 시: terraform init
   ```

3. **Opentofu 변수 검토 및 수정**
   `terraform.tfvars` 파일을 편집하여 배포 설정을 커스터마이즈:
   ```hcl
   project_name = "serverless-handson"       # 프로젝트명
   location     = "koreacentral"             # 원하시는 리전
   apim_publisher_email = "your-email@example.com"
   ```

4. **배포 계획 확인**
   ```bash
   tofu plan -out=tfplan  # Terraform 사용 시: terraform plan -out=tfplan
   ```

5. **설정 적용**
   ```bash
   tofu apply tfplan      # Terraform 사용 시: terraform apply tfplan
   ```

## 📁 프로젝트 구조

```
terraform/
├── main.tf                  # 메인 오케스트레이션
├── variables.tf             # 변수 정의
├── outputs.tf               # 출력 정의
├── backend.tf               # 원격 상태 설정 (선택사항)
├── terraform.tfvars         # 변수 값
├── modules/
│   ├── resource_group/      # 리소스 그룹 모듈
│   ├── storage/             # Storage 계정 모듈
│   ├── eventhub/            # Event Hub 모듈
│   ├── cosmosdb/            # Cosmos DB 모듈
│   ├── function_app/        # Function App 모듈
│   ├── apim/                # API Management 모듈
│   └── insights/            # Application Insights 모듈
└── env/
    └── dev.tfvars           # 환경별 변수
```

## 🔧 설정

### 주요 변수

| 변수 | 설명 | 기본값 |
|------|------|--------|
| `project_name` | 프로젝트 이름 접두사 | `serverless-handson` |
| `environment` | 환경 이름 | `dev` |
| `location` | Azure 리전 | `koreacentral` |
| `eventhub_sku` | Event Hub SKU | `Standard` |
| `cosmos_enable_free_tier` | Cosmos 무료 계층 활성화 | `false` |
| `apim_sku` | APIM SKU | `Consumption` |

### 출력 값

배포 후 중요한 정보가 출력됩니다:

```bash
tofu output  # Terraform 사용 시: terraform output
```

주요 출력 값:
- `resource_group_name` - 생성된 리소스 그룹 이름
- `eventhub_namespace_fqdn` - Event Hub 네임스페이스 FQDN (.env 파일용)
- `cosmosdb_endpoint` - Cosmos DB 엔드포인트 (Managed Identity 인증용)
- `function_app_url` - Function App URL
- `apim_gateway_url` - API Management 게이트웨이 URL


## 🔐 보안 모범 사례

1. **원격 상태 활성화** (팀 작업 시 권장)
   - `backend.tf`에서 백엔드 설정 주석 해제
   - 상태 파일을 위한 Azure Storage 생성
   - `tofu init -migrate-state` 실행 (Terraform 사용 시: `terraform init -migrate-state`)
   - 로컬에서 관리하신다면, 상태 파일을 **몹시** 소중하게 다루어 주셔야 합니다. 

2. **민감한 데이터 보호**
   - `.tfstate` 또는 `.tfstate.backup` 파일 절대 커밋 금지
   - 시크릿은 Azure Key Vault 사용하기
   - 모든 리소스에 RBAC 활성화(Azure Storage Account의 경우, Data Plane 별도)

3. **네트워크 보안**
   - Function App에 VNet 통합 구성
   - Cosmos DB에 프라이빗 엔드포인트 활성화
   - Azure Firewall 또는 NSG 사용

## 🧹 리소스 정리

모든 리소스 삭제:

```bash
tofu destroy  # Terraform 사용 시: terraform destroy
```


## 📖 참고 자료

- [Azure Terraform Provider 문서](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs)
- [OpenTofu 문서](https://opentofu.org/docs/)
- [Azure Functions 문서](https://docs.microsoft.com/en-us/azure/azure-functions/)
- [Event Hubs 문서](https://docs.microsoft.com/en-us/azure/event-hubs/)
- [Cosmos DB 문서](https://docs.microsoft.com/en-us/azure/cosmos-db/)

## 📝 라이선스

MIT License
