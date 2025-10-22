"""
Azure Functions Application
Python v2 Programming Model - 모든 함수를 하나의 파일에 정의
"""
import azure.functions as func
import logging
import json
from datetime import datetime
from typing import List

# Function App 인스턴스 생성 (단 하나만!)
app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)

logger = logging.getLogger(__name__)

# ============================================================
# HTTP Triggers
# ============================================================

@app.route(route="HttpTrigger", methods=["GET", "POST"])
def http_trigger(req: func.HttpRequest) -> func.HttpResponse:
    """
    HTTP Trigger - 기본 테스트용
    GET /api/HttpTrigger?name=Test
    """
    logger.info('HTTP trigger function processing request')
    
    name = req.params.get('name')
    if not name:
        try:
            req_body = req.get_json()
            name = req_body.get('name')
        except ValueError:
            pass
    
    if name:
        return func.HttpResponse(
            json.dumps({
                "message": f"Hello, {name}! This HTTP triggered function executed successfully.",
                "timestamp": datetime.utcnow().isoformat()
            }),
            status_code=200,
            mimetype="application/json"
        )
    else:
        return func.HttpResponse(
            json.dumps({
                "error": "Please pass a name on the query string or in the request body"
            }),
            status_code=400,
            mimetype="application/json"
        )


@app.route(route="process-event", methods=["POST"])
@app.cosmos_db_output(
    arg_name="outputDocument",
    database_name="serverless_db",
    container_name="events",
    connection="CosmosDBConnection"
)
def http_trigger_process_event(
    req: func.HttpRequest,
    outputDocument: func.Out[func.Document]
) -> func.HttpResponse:
    """
    HTTP Trigger Function - APIM에서 호출
    요청 데이터를 처리하고 Cosmos DB에 저장
    
    Endpoint: POST /api/process-event
    """
    logger.info('HTTP trigger function processing request')
    
    try:
        # 요청 본문 파싱
        req_body = req.get_json()
        
        if not req_body:
            return func.HttpResponse(
                json.dumps({"error": "Request body is required"}),
                status_code=400,
                mimetype="application/json"
            )
        
        # 이벤트 데이터 검증
        if "id" not in req_body or "deviceId" not in req_body:
            return func.HttpResponse(
                json.dumps({"error": "Missing required fields: id, deviceId"}),
                status_code=400,
                mimetype="application/json"
            )
        
        # Cosmos DB 문서 준비
        document = {
            "id": req_body["id"],
            "deviceId": req_body["deviceId"],
            "eventType": req_body.get("eventType", "unknown"),
            "timestamp": req_body.get("timestamp", datetime.utcnow().isoformat()),
            "data": req_body.get("data", {}),
            "location": req_body.get("location", {}),
            "processedAt": datetime.utcnow().isoformat(),
            "source": "http-trigger",
            "status": "processed"
        }
        
        # Cosmos DB에 출력 (Output Binding)
        outputDocument.set(func.Document.from_dict(document))
        
        logger.info(f"Successfully processed event {document['id']} from device {document['deviceId']}")
        
        # 성공 응답
        response_data = {
            "status": "success",
            "message": "Event processed successfully",
            "eventId": document["id"],
            "processedAt": document["processedAt"]
        }
        
        return func.HttpResponse(
            json.dumps(response_data),
            status_code=200,
            mimetype="application/json"
        )
        
    except ValueError as e:
        logger.error(f"Invalid JSON in request body: {e}")
        return func.HttpResponse(
            json.dumps({"error": "Invalid JSON format"}),
            status_code=400,
            mimetype="application/json"
        )
    except Exception as e:
        logger.error(f"Error processing event: {e}", exc_info=True)
        return func.HttpResponse(
            json.dumps({"error": "Internal server error"}),
            status_code=500,
            mimetype="application/json"
        )


@app.route(route="health", methods=["GET"])
def health_check(req: func.HttpRequest) -> func.HttpResponse:
    """
    Health Check Endpoint
    APIM Backend Health Probe용
    
    Endpoint: GET /api/health
    """
    logger.info('Health check request received')
    
    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "azure-functions-app"
    }
    
    return func.HttpResponse(
        json.dumps(health_status),
        status_code=200,
        mimetype="application/json"
    )


# ============================================================
# Event Hub Triggers
# ============================================================

@app.event_hub_message_trigger(
    arg_name="events",
    event_hub_name="telemetry_events",
    connection="EventHubConnection",
    cardinality="many"
)
@app.cosmos_db_output(
    arg_name="outputDocuments",
    database_name="serverless_db",
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
    # events를 리스트로 변환 (단일 이벤트일 수도 있음)
    event_list = events if isinstance(events, list) else [events]
    logger.info(f'EventHub trigger function processing {len(event_list)} events')
    
    processed_documents = []
    
    for event in event_list:
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


# ============================================================
# Cosmos DB Change Feed Triggers
# ============================================================

@app.cosmos_db_trigger(
    arg_name="documents",
    database_name="serverless_db",
    container_name="events",
    connection="CosmosDBConnection",
    lease_container_name="leases",
    create_lease_container_if_not_exists=False
)
def cosmosdb_changefeed_processor(documents: func.DocumentList) -> None:
    """
    Cosmos DB Change Feed Trigger Function
    Cosmos DB 변경사항을 실시간으로 감지하고 처리
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
                
                # 비즈니스 로직: 특정 이벤트 타입 처리
                if event_type == "telemetry":
                    data = doc_dict.get("data", {})
                    temperature = data.get("temperature", 0)
                    
                    # 임계값 체크
                    TEMP_THRESHOLD = 40
                    if temperature > TEMP_THRESHOLD:
                        logger.warning(
                            f"Temperature threshold exceeded: {temperature}°C "
                            f"(threshold: {TEMP_THRESHOLD}°C) - Device: {device_id}"
                        )
                
            except Exception as e:
                logger.error(f"Error processing document change: {e}", exc_info=True)
    else:
        logger.warning("Change Feed trigger called with no documents")
