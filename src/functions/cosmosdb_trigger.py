"""
Azure Functions - Cosmos DB Change Feed Trigger
Cosmos DB Change Feed → Function 플로우
AWS DynamoDB Streams → Lambda 마이그레이션 패턴
"""
import azure.functions as func
import logging
import json
from datetime import datetime
from typing import List

app = func.FunctionApp()

logger = logging.getLogger(__name__)


@app.cosmos_db_trigger(
    arg_name="documents",
    database_name="serverless-db",
    container_name="events",
    connection="CosmosDBConnection",
    lease_container_name="leases",
    create_lease_container_if_not_exists=True
)
def cosmosdb_changefeed_processor(documents: func.DocumentList) -> None:
    """
    Cosmos DB Change Feed Trigger Function
    Cosmos DB 변경사항을 실시간으로 감지하고 처리
    
    AWS DynamoDB Streams와 동일한 패턴:
    - 문서 생성/수정 감지
    - 변경 로그 저장
    - 후속 처리 트리거 (AI Enrichment, 알림 등)
    """
    if documents:
        logger.info(f'Cosmos DB Change Feed triggered with {len(documents)} document(s)')
        
        for doc in documents:
            try:
                # 문서 데이터 추출
                doc_dict = json.loads(doc.to_json())
                
                event_id = doc_dict.get("id", "unknown")
                device_id = doc_dict.get("deviceId", "unknown")
                event_type = doc_dict.get("eventType", "unknown")
                
                logger.info(
                    f"Change detected - ID: {event_id}, "
                    f"Device: {device_id}, Type: {event_type}"
                )
                
                # 변경 유형 분석 (새 문서 vs 수정)
                # Cosmos DB는 _ts (timestamp) 필드로 변경 시점 추적
                timestamp = doc_dict.get("_ts", 0)
                
                # 비즈니스 로직 예제: 특정 이벤트 타입 처리
                if event_type == "telemetry":
                    process_telemetry_change(doc_dict)
                elif event_type == "alert":
                    process_alert_change(doc_dict)
                else:
                    logger.info(f"Unhandled event type: {event_type}")
                
                # AI Enrichment 트리거 (향후 구현)
                # trigger_ai_enrichment(doc_dict)
                
            except Exception as e:
                logger.error(f"Error processing document change: {e}", exc_info=True)
    else:
        logger.warning("Change Feed trigger called with no documents")


def process_telemetry_change(document: dict) -> None:
    """텔레메트리 이벤트 변경 처리
    
    예제:
    - 온도 임계값 초과시 알림
    - 데이터 집계 및 통계 생성
    - 외부 시스템 연동
    """
    data = document.get("data", {})
    temperature = data.get("temperature", 0)
    
    # 임계값 체크
    TEMP_THRESHOLD = 40
    if temperature > TEMP_THRESHOLD:
        logger.warning(
            f"Temperature threshold exceeded: {temperature}°C "
            f"(threshold: {TEMP_THRESHOLD}°C) - Device: {document.get('deviceId')}"
        )
        # TODO: Send alert to Event Grid or Queue
    
    logger.info(f"Telemetry processed: Temperature={temperature}°C")


def process_alert_change(document: dict) -> None:
    """알림 이벤트 변경 처리
    
    예제:
    - 알림 이력 추적
    - 알림 집계 및 대시보드 업데이트
    """
    alert_level = document.get("data", {}).get("level", "info")
    message = document.get("data", {}).get("message", "No message")
    
    logger.info(f"Alert change processed: Level={alert_level}, Message={message}")


# AI Enrichment 트리거 함수 (추후 구현 예제)
@app.cosmos_db_trigger(
    arg_name="documents",
    database_name="serverless-db",
    container_name="events",
    connection="CosmosDBConnection",
    lease_container_name="ai-enrichment-leases",
    create_lease_container_if_not_exists=True
)
def cosmosdb_ai_enrichment_trigger(documents: func.DocumentList) -> None:
    """
    AI Enrichment Trigger
    Cosmos DB 변경사항을 감지하여 Azure AI Search로 인덱싱
    
    향후 확장:
    - Azure Cognitive Search 인덱싱
    - Azure OpenAI를 통한 데이터 분석
    - 감정 분석, 키워드 추출 등
    """
    if documents:
        logger.info(f'AI Enrichment triggered for {len(documents)} document(s)')
        
        for doc in documents:
            try:
                doc_dict = json.loads(doc.to_json())
                event_id = doc_dict.get("id")
                
                logger.info(f"AI Enrichment processing: {event_id}")
                
                # TODO: Azure AI Search 인덱싱
                # search_client.upload_documents([doc_dict])
                
                # TODO: Azure OpenAI 분석
                # analysis_result = analyze_with_openai(doc_dict)
                
            except Exception as e:
                logger.error(f"AI Enrichment error: {e}", exc_info=True)
