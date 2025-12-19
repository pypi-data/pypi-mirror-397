from abc import ABC, abstractmethod
from typing import Optional, Any
from pyspark.sql import DataFrame
from data_transfer_lib.connections.base import BaseConnection


class BaseReader(ABC):
    def __init__(
        self,
        connection: BaseConnection,
        db_name: str,
        table_name: str,
    ):
        self.connection = connection
        self.db_name = db_name
        self.table_name = table_name
        self._prepare()
    
    @abstractmethod
    def _prepare(self) -> None:
        pass
    
    @abstractmethod
    def start(self) -> DataFrame:
        pass