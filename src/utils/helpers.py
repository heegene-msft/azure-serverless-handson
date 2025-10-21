"""
유틸리티 함수 모음
"""
import json
import logging
from typing import Any, Dict, Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


def format_timestamp(dt: Optional[datetime] = None) -> str:
    """ISO 8601 형식으로 타임스탬프 포맷
    
    Args:
        dt: datetime 객체 (None이면 현재 시간)
    
    Returns:
        ISO 8601 형식 문자열
    """
    if dt is None:
        dt = datetime.utcnow()
    return dt.isoformat() + "Z"


def parse_timestamp(timestamp_str: str) -> Optional[datetime]:
    """ISO 8601 타임스탬프 파싱
    
    Args:
        timestamp_str: ISO 8601 형식 문자열
    
    Returns:
        datetime 객체 또는 None
    """
    try:
        # Z suffix 제거
        if timestamp_str.endswith('Z'):
            timestamp_str = timestamp_str[:-1]
        return datetime.fromisoformat(timestamp_str)
    except ValueError as e:
        logger.error(f"Failed to parse timestamp: {timestamp_str}, error: {e}")
        return None


def safe_json_loads(json_str: str, default: Any = None) -> Any:
    """안전한 JSON 파싱
    
    Args:
        json_str: JSON 문자열
        default: 파싱 실패시 반환할 기본값
    
    Returns:
        파싱된 객체 또는 기본값
    """
    try:
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        logger.error(f"JSON parsing failed: {e}")
        return default


def safe_json_dumps(obj: Any, default: str = "{}") -> str:
    """안전한 JSON 직렬화
    
    Args:
        obj: 직렬화할 객체
        default: 직렬화 실패시 반환할 기본값
    
    Returns:
        JSON 문자열
    """
    try:
        return json.dumps(obj, ensure_ascii=False, default=str)
    except (TypeError, ValueError) as e:
        logger.error(f"JSON serialization failed: {e}")
        return default


def validate_event_data(event: Dict[str, Any]) -> tuple[bool, Optional[str]]:
    """이벤트 데이터 검증
    
    Args:
        event: 검증할 이벤트 딕셔너리
    
    Returns:
        (유효 여부, 에러 메시지)
    """
    required_fields = ["id", "deviceId", "timestamp"]
    
    for field in required_fields:
        if field not in event:
            return False, f"Missing required field: {field}"
    
    # 타임스탬프 검증
    timestamp = parse_timestamp(event["timestamp"])
    if timestamp is None:
        return False, "Invalid timestamp format"
    
    # 미래 시간 체크
    now = datetime.utcnow()
    if timestamp > now + timedelta(minutes=5):
        return False, "Timestamp is in the future"
    
    return True, None


def calculate_latency_ms(start_time: str, end_time: Optional[str] = None) -> float:
    """레이턴시 계산 (밀리초)
    
    Args:
        start_time: 시작 시간 (ISO 8601)
        end_time: 종료 시간 (ISO 8601, None이면 현재 시간)
    
    Returns:
        레이턴시 (밀리초)
    """
    start = parse_timestamp(start_time)
    end = parse_timestamp(end_time) if end_time else datetime.utcnow()
    
    if start is None or end is None:
        return 0.0
    
    delta = end - start
    return delta.total_seconds() * 1000


def retry_with_backoff(func, max_retries: int = 3, initial_delay: float = 1.0):
    """지수 백오프 재시도 데코레이터
    
    Args:
        func: 재시도할 함수
        max_retries: 최대 재시도 횟수
        initial_delay: 초기 지연 시간 (초)
    """
    import time
    from functools import wraps
    
    @wraps(func)
    def wrapper(*args, **kwargs):
        delay = initial_delay
        last_exception = None
        
        for attempt in range(max_retries + 1):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                last_exception = e
                if attempt < max_retries:
                    logger.warning(
                        f"Attempt {attempt + 1}/{max_retries} failed: {e}. "
                        f"Retrying in {delay:.1f}s..."
                    )
                    time.sleep(delay)
                    delay *= 2  # Exponential backoff
                else:
                    logger.error(f"All {max_retries} retry attempts failed")
        
        raise last_exception
    
    return wrapper


class MetricsCollector:
    """간단한 메트릭 수집기"""
    
    def __init__(self):
        self.metrics = {
            "events_sent": 0,
            "events_received": 0,
            "events_processed": 0,
            "events_failed": 0,
            "total_latency_ms": 0.0,
        }
    
    def increment(self, metric_name: str, value: float = 1.0):
        """메트릭 증가"""
        if metric_name in self.metrics:
            self.metrics[metric_name] += value
    
    def record_latency(self, latency_ms: float):
        """레이턴시 기록"""
        self.metrics["total_latency_ms"] += latency_ms
    
    def get_average_latency(self) -> float:
        """평균 레이턴시 계산"""
        if self.metrics["events_processed"] == 0:
            return 0.0
        return self.metrics["total_latency_ms"] / self.metrics["events_processed"]
    
    def get_summary(self) -> Dict[str, Any]:
        """메트릭 요약 반환"""
        return {
            **self.metrics,
            "average_latency_ms": self.get_average_latency(),
            "success_rate": (
                self.metrics["events_processed"] / 
                max(self.metrics["events_received"], 1)
            ) * 100
        }
    
    def reset(self):
        """메트릭 초기화"""
        for key in self.metrics:
            self.metrics[key] = 0 if isinstance(self.metrics[key], int) else 0.0
