"""
Azure Functions - Event Hub Trigger
Event Hub → Function → Cosmos DB 플로우
AWS Lambda + Kinesis 마이그레이션 패턴
"""
import azure.functions as func
import logging
import json
from datetime import datetime
from typing import List

app = func.FunctionApp()

logger = logging.getLogger(__name__)


@app.event_hub_message_trigger(
    arg_name="events",
    event_hub_name="order_events",
    connection="EventHubConnection"
)
@app.cosmos_db_output(
    arg_name="outputDocuments",
    database_name="serverless-db",
    container_name="events",
    connection="CosmosDBConnection"
)
def eventhub_trigger_processor(
    events: List[func.EventHubEvent],
    outputDocuments: func.Out[func.DocumentList]
) -> None:
    """
    Event Hub Trigger Function
    Event Hub에서 메시지를 받아 Cosmos DB에 저장
    """
    logger.info(f'EventHub trigger function processing {len(events)} events')
    
    processed_documents = []
    
    for event in events:
        try:
            # 이벤트 데이터 파싱
            event_body = event.get_body().decode('utf-8')
            event_data = json.loads(event_body)
            
            # 메타데이터 추출
            partition_key = event.partition_key
            sequence_number = event.sequence_number
            enqueued_time = event.enqueued_time
            
            # 문서 생성
            document = {
                "id": event_data.get("id", f"evt-{sequence_number}"),
                "deviceId": event_data.get("deviceId", "unknown"),
                "eventType": event_data.get("eventType", "telemetry"),
                "timestamp": event_data.get("timestamp"),
                "data": event_data.get("data", {}),
                "location": event_data.get("location", {}),
                # Event Hub 메타데이터
                "eventHub": {
                    "partitionKey": partition_key,
                    "sequenceNumber": sequence_number,
                    "enqueuedTime": enqueued_time.isoformat() if enqueued_time else None,
                    "offset": event.offset
                },
                "processedAt": datetime.utcnow().isoformat(),
                "source": "eventhub-trigger",
                "status": "processed"
            }
            
            processed_documents.append(document)
            
            logger.info(
                f"Processed event {document['id']} from partition {partition_key}, "
                f"sequence {sequence_number}"
            )
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse event JSON: {e}")
            continue
        except Exception as e:
            logger.error(f"Error processing event: {e}", exc_info=True)
            continue
    
    # Cosmos DB에 일괄 저장 (Output Binding)
    if processed_documents:
        output_docs = [func.Document.from_dict(doc) for doc in processed_documents]
        outputDocuments.set(output_docs)
        logger.info(f"Successfully saved {len(processed_documents)} documents to Cosmos DB")
    else:
        logger.warning("No documents to save")


@app.event_hub_message_trigger(
    arg_name="events",
    event_hub_name="alerts-hub",
    connection="EventHubConnection"
)
def eventhub_alert_processor(events: List[func.EventHubEvent]) -> None:
    """
    Alert Event Hub Trigger Function
    알림 이벤트 처리 (로깅, 외부 API 호출 등)
    
    Cosmos DB 저장 없이 실시간 알림만 처리하는 예제
    """
    logger.info(f'Alert processor received {len(events)} alerts')
    
    for event in events:
        try:
            event_body = event.get_body().decode('utf-8')
            alert_data = json.loads(event_body)
            
            # 알림 수준에 따라 처리
            alert_level = alert_data.get("level", "info")
            message = alert_data.get("message", "No message")
            
            if alert_level == "critical":
                logger.critical(f"CRITICAL ALERT: {message}")
                # TODO: 외부 알림 시스템 호출 (PagerDuty, Teams 등)
            elif alert_level == "warning":
                logger.warning(f"WARNING: {message}")
            else:
                logger.info(f"INFO: {message}")
                
        except Exception as e:
            logger.error(f"Error processing alert: {e}")
