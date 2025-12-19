from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from pyspark.sql import SparkSession

class BaseConnection(ABC):
    def __init__(
        self,
        host: str,
        port: int,
        user: str,
        password: str,
        database: Optional[str] = None,
        spark: Optional[SparkSession] = None,
    ):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.database = database
        self.spark = spark or self._get_or_create_spark()
    
    @abstractmethod
    def get_jdbc_url(self) -> str:
        pass
    
    @abstractmethod
    def get_connection_properties(self) -> Dict[str, str]:
        pass
    
    @abstractmethod
    def test_connection(self) -> bool:
        pass
    
    @abstractmethod
    def get_table_schema(self, db_name: str, table_name: str) -> Dict[str, Any]:
        pass
    
    def _get_or_create_spark(self) -> SparkSession:
        return SparkSession.builder.getOrCreate()