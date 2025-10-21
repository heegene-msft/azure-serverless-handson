"""
Azure 리소스 연결 설정 및 클라이언트 초기화
"""
import os
from typing import Optional
from dataclasses import dataclass
from azure.eventhub import EventHubProducerClient
from azure.cosmos import CosmosClient
from azure.identity import DefaultAzureCredential
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class AzureConfig:
    """Azure 서비스 연결 정보"""
    # Event Hub
    eventhub_namespace: str
    eventhub_name: str
    eventhub_connection_string: Optional[str] = None
    
    # Cosmos DB
    cosmos_endpoint: str
    cosmos_database: str
    cosmos_container: str
    cosmos_connection_string: Optional[str] = None
    
    # API Management
    apim_gateway_url: str
    
    # Storage Account
    storage_connection_string: str
    storage_container: str = "test-data"
    
    # Application Insights
    appinsights_connection_string: Optional[str] = None
    
    @classmethod
    def from_env(cls) -> "AzureConfig":
        """환경변수에서 설정 로드"""
        return cls(
            eventhub_namespace=os.getenv("EVENTHUB_NAMESPACE", ""),
            eventhub_name=os.getenv("EVENTHUB_NAME", ""),
            eventhub_connection_string=os.getenv("EVENTHUB_CONNECTION_STRING"),
            cosmos_endpoint=os.getenv("COSMOS_ENDPOINT", ""),
            cosmos_database=os.getenv("COSMOS_DATABASE", ""),
            cosmos_container=os.getenv("COSMOS_CONTAINER", ""),
            cosmos_connection_string=os.getenv("COSMOS_CONNECTION_STRING"),
            apim_gateway_url=os.getenv("APIM_GATEWAY_URL", ""),
            storage_connection_string=os.getenv("STORAGE_CONNECTION_STRING", ""),
            storage_container=os.getenv("STORAGE_CONTAINER", "test-data"),
            appinsights_connection_string=os.getenv("APPINSIGHTS_CONNECTION_STRING")
        )


class AzureClientFactory:
    """Azure 클라이언트 팩토리 - 싱글톤 패턴"""
    
    _eventhub_producer: Optional[EventHubProducerClient] = None
    _cosmos_client: Optional[CosmosClient] = None
    _config: Optional[AzureConfig] = None
    
    @classmethod
    def initialize(cls, config: AzureConfig):
        """클라이언트 초기화"""
        cls._config = config
        logger.info("Azure clients initialized")
    
    @classmethod
    def get_eventhub_producer(cls) -> EventHubProducerClient:
        """Event Hub Producer 클라이언트 반환"""
        if cls._eventhub_producer is None:
            if not cls._config:
                raise ValueError("AzureClientFactory not initialized")
            
            if cls._config.eventhub_connection_string:
                # Connection String 사용
                cls._eventhub_producer = EventHubProducerClient.from_connection_string(
                    conn_str=cls._config.eventhub_connection_string,
                    eventhub_name=cls._config.eventhub_name
                )
            else:
                # DefaultAzureCredential 사용 (Passwordless)
                credential = DefaultAzureCredential()
                cls._eventhub_producer = EventHubProducerClient(
                    fully_qualified_namespace=cls._config.eventhub_namespace,
                    eventhub_name=cls._config.eventhub_name,
                    credential=credential
                )
            
            logger.info(f"EventHub Producer connected to {cls._config.eventhub_name}")
        
        return cls._eventhub_producer
    
    @classmethod
    def get_cosmos_client(cls) -> CosmosClient:
        """Cosmos DB 클라이언트 반환"""
        if cls._cosmos_client is None:
            if not cls._config:
                raise ValueError("AzureClientFactory not initialized")
            
            if cls._config.cosmos_connection_string:
                # Connection String 사용
                cls._cosmos_client = CosmosClient.from_connection_string(
                    cls._config.cosmos_connection_string
                )
            else:
                # DefaultAzureCredential 사용 (RBAC)
                credential = DefaultAzureCredential()
                cls._cosmos_client = CosmosClient(
                    url=cls._config.cosmos_endpoint,
                    credential=credential
                )
            
            logger.info(f"Cosmos DB client connected to {cls._config.cosmos_endpoint}")
        
        return cls._cosmos_client
    
    @classmethod
    def close_all(cls):
        """모든 클라이언트 종료"""
        if cls._eventhub_producer:
            cls._eventhub_producer.close()
            logger.info("EventHub Producer closed")
        
        # Cosmos Client는 자동으로 관리됨 (context manager 사용 권장)
        logger.info("All Azure clients closed")
