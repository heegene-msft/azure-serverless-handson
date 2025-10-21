"""
Event Hub Producer - 이벤트 생성 및 전송
AWS Kinesis → Azure Event Hub 마이그레이션 패턴
"""
import json
import uuid
import asyncio
from datetime import datetime
from typing import List, Dict, Any
from azure.eventhub import EventData, EventHubProducerClient
from azure.eventhub.exceptions import EventHubError
import logging

logger = logging.getLogger(__name__)


class EventProducer:
    """Event Hub로 이벤트를 전송하는 Producer"""
    
    def __init__(self, producer_client: EventHubProducerClient):
        """
        Args:
            producer_client: EventHubProducerClient 인스턴스
        """
        self.producer = producer_client
    
    def create_sample_event(self, device_id: str = None) -> Dict[str, Any]:
        """샘플 이벤트 데이터 생성 (IoT 텔레메트리 시뮬레이션)
        
        Args:
            device_id: 디바이스 ID (없으면 자동 생성)
        
        Returns:
            이벤트 데이터 딕셔너리
        """
        if device_id is None:
            device_id = str(uuid.uuid4())
        
        return {
            "id": str(uuid.uuid4()),
            "deviceId": device_id,
            "timestamp": datetime.utcnow().isoformat(),
            "eventType": "telemetry",
            "data": {
                "temperature": 20 + (hash(device_id) % 30),  # 20-50°C
                "humidity": 40 + (hash(device_id) % 40),     # 40-80%
                "pressure": 1000 + (hash(device_id) % 50),   # 1000-1050 hPa
            },
            "location": {
                "region": "koreacentral",
                "facility": f"facility-{hash(device_id) % 5}"
            }
        }
    
    def send_events_sync(self, events: List[Dict[str, Any]], partition_key: str = None) -> int:
        """동기적으로 이벤트 배치 전송 (Connection String 방식)
        
        Args:
            events: 전송할 이벤트 리스트
            partition_key: 파티션 키 (선택사항)
        
        Returns:
            전송된 이벤트 수
        """
        if not events:
            logger.warning("No events to send")
            return 0
        
        try:
            # 배치 생성
            event_data_batch = self.producer.create_batch(
                partition_key=partition_key if partition_key else None
            )
            
            # 이벤트 추가
            sent_count = 0
            for event in events:
                event_json = json.dumps(event)
                event_data = EventData(event_json)
                
                # 커스텀 속성 추가 (APIM에서 활용 가능)
                event_data.properties = {
                    "eventType": event.get("eventType", "unknown"),
                    "deviceId": event.get("deviceId", "unknown")
                }
                
                try:
                    event_data_batch.add(event_data)
                    sent_count += 1
                except ValueError:
                    # 배치가 꽉 찬 경우 먼저 전송
                    logger.info(f"Batch full, sending {sent_count} events...")
                    self.producer.send_batch(event_data_batch)
                    
                    # 새 배치 생성 후 현재 이벤트 추가
                    event_data_batch = self.producer.create_batch(partition_key=partition_key)
                    event_data_batch.add(event_data)
                    sent_count = 1
            
            # 남은 이벤트 전송
            if sent_count > 0:
                self.producer.send_batch(event_data_batch)
                logger.info(f"Successfully sent {sent_count} events to Event Hub")
            
            return sent_count
            
        except EventHubError as e:
            logger.error(f"Failed to send events: {e}")
            raise
    
    def send_single_event(self, event: Dict[str, Any], partition_key: str = None) -> bool:
        """단일 이벤트 전송
        
        Args:
            event: 전송할 이벤트
            partition_key: 파티션 키
        
        Returns:
            성공 여부
        """
        try:
            return self.send_events_sync([event], partition_key) == 1
        except Exception as e:
            logger.error(f"Failed to send single event: {e}")
            return False
    
    def close(self):
        """Producer 연결 종료"""
        self.producer.close()
        logger.info("EventHub Producer connection closed")


class AsyncEventProducer:
    """비동기 Event Hub Producer (높은 처리량 요구시 사용)"""
    
    def __init__(self, eventhub_namespace: str, eventhub_name: str, credential):
        """
        Args:
            eventhub_namespace: Event Hub 네임스페이스 FQDN
            eventhub_name: Event Hub 이름
            credential: Azure 인증 정보 (DefaultAzureCredential 등)
        """
        from azure.eventhub.aio import EventHubProducerClient
        
        self.producer = EventHubProducerClient(
            fully_qualified_namespace=eventhub_namespace,
            eventhub_name=eventhub_name,
            credential=credential
        )
    
    async def send_events_async(self, events: List[Dict[str, Any]], partition_key: str = None) -> int:
        """비동기적으로 이벤트 배치 전송
        
        Args:
            events: 전송할 이벤트 리스트
            partition_key: 파티션 키
        
        Returns:
            전송된 이벤트 수
        """
        if not events:
            return 0
        
        async with self.producer:
            event_data_batch = await self.producer.create_batch(
                partition_key=partition_key if partition_key else None
            )
            
            sent_count = 0
            for event in events:
                event_json = json.dumps(event)
                event_data = EventData(event_json)
                event_data.properties = {
                    "eventType": event.get("eventType", "unknown"),
                    "deviceId": event.get("deviceId", "unknown")
                }
                
                try:
                    event_data_batch.add(event_data)
                    sent_count += 1
                except ValueError:
                    await self.producer.send_batch(event_data_batch)
                    event_data_batch = await self.producer.create_batch(partition_key=partition_key)
                    event_data_batch.add(event_data)
                    sent_count = 1
            
            if sent_count > 0:
                await self.producer.send_batch(event_data_batch)
                logger.info(f"Async sent {sent_count} events")
            
            return sent_count


# CLI 실행 예제
if __name__ == "__main__":
    import os
    from azure.eventhub import EventHubProducerClient
    
    # 환경변수 확인
    connection_string = os.getenv("EVENTHUB_CONNECTION_STRING")
    eventhub_name = os.getenv("EVENTHUB_NAME", "telemetry-hub")
    
    if not connection_string:
        print("Error: EVENTHUB_CONNECTION_STRING not set")
        exit(1)
    
    # Producer 생성
    producer_client = EventHubProducerClient.from_connection_string(
        conn_str=connection_string,
        eventhub_name=eventhub_name
    )
    
    event_producer = EventProducer(producer_client)
    
    # 샘플 이벤트 생성 및 전송
    device_ids = [f"device-{i:03d}" for i in range(1, 6)]
    events = [event_producer.create_sample_event(device_id) for device_id in device_ids]
    
    print(f"Sending {len(events)} events to Event Hub...")
    sent_count = event_producer.send_events_sync(events)
    print(f"Successfully sent {sent_count} events")
    
    event_producer.close()
