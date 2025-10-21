"""
유닛 테스트 - Event Producer
"""
import pytest
import json
from datetime import datetime
from unittest.mock import Mock, MagicMock, patch
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.producer.event_producer import EventProducer


class TestEventProducer:
    """EventProducer 클래스 유닛 테스트"""
    
    @pytest.fixture
    def mock_producer_client(self):
        """Mock EventHubProducerClient"""
        mock_client = MagicMock()
        mock_batch = MagicMock()
        mock_client.create_batch.return_value = mock_batch
        return mock_client
    
    @pytest.fixture
    def event_producer(self, mock_producer_client):
        """EventProducer 인스턴스"""
        return EventProducer(mock_producer_client)
    
    def test_create_sample_event_with_device_id(self, event_producer):
        """디바이스 ID로 샘플 이벤트 생성 테스트"""
        device_id = "test-device-001"
        event = event_producer.create_sample_event(device_id)
        
        assert event["deviceId"] == device_id
        assert "id" in event
        assert "timestamp" in event
        assert "eventType" in event
        assert event["eventType"] == "telemetry"
        assert "data" in event
        assert "temperature" in event["data"]
        assert "humidity" in event["data"]
        assert "pressure" in event["data"]
    
    def test_create_sample_event_auto_device_id(self, event_producer):
        """자동 디바이스 ID 생성 테스트"""
        event = event_producer.create_sample_event()
        
        assert "deviceId" in event
        assert event["deviceId"] is not None
        assert len(event["deviceId"]) > 0
    
    def test_send_events_sync_empty_list(self, event_producer):
        """빈 이벤트 리스트 전송 테스트"""
        result = event_producer.send_events_sync([])
        
        assert result == 0
        event_producer.producer.create_batch.assert_not_called()
    
    def test_send_events_sync_success(self, event_producer, mock_producer_client):
        """이벤트 전송 성공 테스트"""
        events = [
            {"id": "1", "deviceId": "device1", "eventType": "telemetry", "data": {}},
            {"id": "2", "deviceId": "device2", "eventType": "telemetry", "data": {}},
        ]
        
        # Mock batch가 모든 이벤트를 받도록 설정
        mock_batch = mock_producer_client.create_batch.return_value
        mock_batch.add.return_value = None
        
        result = event_producer.send_events_sync(events)
        
        assert result == 2
        assert mock_batch.add.call_count == 2
        mock_producer_client.send_batch.assert_called_once()
    
    def test_send_single_event(self, event_producer):
        """단일 이벤트 전송 테스트"""
        event = {"id": "1", "deviceId": "device1", "eventType": "telemetry", "data": {}}
        
        result = event_producer.send_single_event(event)
        
        assert isinstance(result, bool)


class TestEventValidation:
    """이벤트 데이터 검증 테스트"""
    
    def test_event_structure(self):
        """이벤트 구조 검증"""
        from src.utils import validate_event_data
        
        valid_event = {
            "id": "test-id",
            "deviceId": "device-001",
            "timestamp": datetime.utcnow().isoformat(),
            "data": {}
        }
        
        is_valid, error = validate_event_data(valid_event)
        assert is_valid is True
        assert error is None
    
    def test_missing_required_fields(self):
        """필수 필드 누락 검증"""
        from src.utils import validate_event_data
        
        invalid_event = {
            "id": "test-id"
            # deviceId, timestamp 누락
        }
        
        is_valid, error = validate_event_data(invalid_event)
        assert is_valid is False
        assert error is not None
        assert "Missing required field" in error


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
