"""
Azure Functions - HTTP Trigger
APIM → Function → Cosmos DB 플로우
"""
import azure.functions as func
import logging
import json
from datetime import datetime
from typing import Dict, Any

app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)

logger = logging.getLogger(__name__)


@app.route(route="process-event", methods=["POST"])
@app.cosmos_db_output(
    arg_name="outputDocument",
    database_name="serverless-db",
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
        "service": "azure-functions-http-trigger"
    }
    
    return func.HttpResponse(
        json.dumps(health_status),
        status_code=200,
        mimetype="application/json"
    )
