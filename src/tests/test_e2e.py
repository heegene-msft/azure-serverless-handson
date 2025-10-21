"""
E2E (End-to-End) 통합 테스트
전체 플로우 검증: Event → EventHub → APIM → Function → CosmosDB
"""
import os
import sys
import json
import time
import logging
from typing import List, Dict, Any
from datetime import datetime, timedelta

# 프로젝트 루트를 Python path에 추가
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.config import AzureConfig, AzureClientFactory
from src.producer import EventProducer
from src.utils import MetricsCollector, calculate_latency_ms

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class E2ETestRunner:
    """E2E 테스트 실행기"""
    
    def __init__(self):
        """테스트 환경 초기화"""
        logger.info("Initializing E2E test environment...")
        
        # Azure 설정 로드
        self.config = AzureConfig.from_env()
        AzureClientFactory.initialize(self.config)
        
        # Event Producer 생성
        producer_client = AzureClientFactory.get_eventhub_producer()
        self.event_producer = EventProducer(producer_client)
        
        # Cosmos DB 클라이언트
        self.cosmos_client = AzureClientFactory.get_cosmos_client()
        self.cosmos_database = self.cosmos_client.get_database_client(
            self.config.cosmos_database
        )
        self.cosmos_container = self.cosmos_database.get_container_client(
            self.config.cosmos_container
        )
        
        # 메트릭 수집기
        self.metrics = MetricsCollector()
        
        logger.info("E2E test environment ready")
    
    def test_event_to_eventhub(self, num_events: int = 5) -> List[Dict[str, Any]]:
        """테스트 1: Event Hub로 이벤트 전송
        
        Args:
            num_events: 전송할 이벤트 수
        
        Returns:
            전송된 이벤트 리스트
        """
        logger.info(f"\n{'='*60}")
        logger.info(f"TEST 1: Sending {num_events} events to Event Hub")
        logger.info(f"{'='*60}")
        
        # 테스트 이벤트 생성
        device_ids = [f"test-device-{i:03d}" for i in range(num_events)]
        events = [
            self.event_producer.create_sample_event(device_id) 
            for device_id in device_ids
        ]
        
        # 전송 시작 시간 기록
        start_time = datetime.utcnow()
        
        # Event Hub로 전송
        sent_count = self.event_producer.send_events_sync(events)
        
        # 메트릭 기록
        self.metrics.increment("events_sent", sent_count)
        
        logger.info(f"✅ Successfully sent {sent_count}/{num_events} events")
        logger.info(f"Event IDs: {[e['id'][:8] + '...' for e in events[:3]]}")
        
        return events
    
    def test_eventhub_to_cosmosdb(
        self, 
        event_ids: List[str], 
        max_wait_seconds: int = 30
    ) -> bool:
        """테스트 2: Event Hub → Function → Cosmos DB 검증
        
        Args:
            event_ids: 검증할 이벤트 ID 리스트
            max_wait_seconds: 최대 대기 시간 (초)
        
        Returns:
            모든 이벤트가 Cosmos DB에 저장되었는지 여부
        """
        logger.info(f"\n{'='*60}")
        logger.info(f"TEST 2: Verifying events in Cosmos DB")
        logger.info(f"{'='*60}")
        
        logger.info(f"Waiting for Function to process events (max {max_wait_seconds}s)...")
        
        found_events = set()
        wait_interval = 2
        elapsed = 0
        
        while elapsed < max_wait_seconds:
            time.sleep(wait_interval)
            elapsed += wait_interval
            
            # Cosmos DB에서 이벤트 조회
            for event_id in event_ids:
                if event_id in found_events:
                    continue
                
                try:
                    query = f"SELECT * FROM c WHERE c.id = '{event_id}'"
                    items = list(self.cosmos_container.query_items(
                        query=query,
                        enable_cross_partition_query=True
                    ))
                    
                    if items:
                        found_events.add(event_id)
                        self.metrics.increment("events_processed")
                        logger.info(f"✅ Found event {event_id[:8]}... in Cosmos DB")
                
                except Exception as e:
                    logger.error(f"Error querying Cosmos DB: {e}")
            
            # 모든 이벤트를 찾으면 종료
            if len(found_events) == len(event_ids):
                break
            
            logger.info(f"Progress: {len(found_events)}/{len(event_ids)} events found ({elapsed}s elapsed)")
        
        # 결과 요약
        success = len(found_events) == len(event_ids)
        
        if success:
            logger.info(f"✅ All {len(event_ids)} events verified in Cosmos DB")
        else:
            missing = len(event_ids) - len(found_events)
            logger.warning(f"⚠️  {missing} events not found in Cosmos DB")
            self.metrics.increment("events_failed", missing)
        
        return success
    
    def test_apim_http_endpoint(self, num_requests: int = 3) -> bool:
        """테스트 3: APIM → HTTP Trigger Function → Cosmos DB
        
        Args:
            num_requests: 전송할 요청 수
        
        Returns:
            모든 요청이 성공했는지 여부
        """
        logger.info(f"\n{'='*60}")
        logger.info(f"TEST 3: Testing APIM HTTP endpoint")
        logger.info(f"{'='*60}")
        
        import requests
        
        apim_url = self.config.apim_gateway_url
        if not apim_url:
            logger.warning("⚠️  APIM Gateway URL not configured, skipping test")
            return False
        
        endpoint = f"{apim_url}/process-event"
        success_count = 0
        
        for i in range(num_requests):
            # 테스트 이벤트 생성
            event = self.event_producer.create_sample_event(f"apim-test-{i}")
            
            try:
                response = requests.post(
                    endpoint,
                    json=event,
                    timeout=10
                )
                
                if response.status_code == 200:
                    success_count += 1
                    logger.info(f"✅ Request {i+1}/{num_requests} successful: {response.json()}")
                else:
                    logger.error(f"❌ Request {i+1} failed: {response.status_code} - {response.text}")
            
            except requests.exceptions.RequestException as e:
                logger.error(f"❌ Request {i+1} error: {e}")
        
        success = success_count == num_requests
        
        if success:
            logger.info(f"✅ All {num_requests} APIM requests successful")
        else:
            logger.warning(f"⚠️  {num_requests - success_count} APIM requests failed")
        
        return success
    
    def run_all_tests(self) -> Dict[str, Any]:
        """모든 E2E 테스트 실행
        
        Returns:
            테스트 결과 요약
        """
        logger.info(f"\n{'#'*60}")
        logger.info(f"# Starting E2E Test Suite")
        logger.info(f"{'#'*60}")
        
        test_results = {
            "start_time": datetime.utcnow().isoformat(),
            "tests_passed": 0,
            "tests_failed": 0,
            "tests": []
        }
        
        try:
            # Test 1: Event Hub 전송
            events = self.test_event_to_eventhub(num_events=5)
            event_ids = [e["id"] for e in events]
            test_results["tests"].append({
                "name": "EventHub Send",
                "status": "PASSED",
                "events_sent": len(events)
            })
            test_results["tests_passed"] += 1
            
            # Test 2: Cosmos DB 검증
            cosmos_success = self.test_eventhub_to_cosmosdb(event_ids)
            test_results["tests"].append({
                "name": "EventHub to CosmosDB",
                "status": "PASSED" if cosmos_success else "FAILED"
            })
            if cosmos_success:
                test_results["tests_passed"] += 1
            else:
                test_results["tests_failed"] += 1
            
            # Test 3: APIM 엔드포인트 (선택적)
            # apim_success = self.test_apim_http_endpoint(num_requests=3)
            # test_results["tests"].append({
            #     "name": "APIM HTTP Endpoint",
            #     "status": "PASSED" if apim_success else "FAILED"
            # })
            
        except Exception as e:
            logger.error(f"Test suite error: {e}", exc_info=True)
            test_results["tests_failed"] += 1
            test_results["error"] = str(e)
        
        finally:
            # 메트릭 요약
            test_results["metrics"] = self.metrics.get_summary()
            test_results["end_time"] = datetime.utcnow().isoformat()
            
            # 정리
            self.cleanup()
        
        return test_results
    
    def cleanup(self):
        """테스트 환경 정리"""
        logger.info("\nCleaning up test environment...")
        AzureClientFactory.close_all()
        logger.info("Cleanup complete")


def main():
    """E2E 테스트 메인 함수"""
    runner = E2ETestRunner()
    results = runner.run_all_tests()
    
    # 결과 출력
    logger.info(f"\n{'#'*60}")
    logger.info(f"# E2E Test Results")
    logger.info(f"{'#'*60}")
    logger.info(json.dumps(results, indent=2))
    
    # 종료 코드 반환
    sys.exit(0 if results["tests_failed"] == 0 else 1)


if __name__ == "__main__":
    main()
