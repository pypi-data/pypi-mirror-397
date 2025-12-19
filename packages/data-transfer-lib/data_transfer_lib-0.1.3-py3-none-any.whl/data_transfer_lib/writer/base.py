from abc import ABC, abstractmethod
from pyspark.sql import DataFrame
from data_transfer_lib.connections.base import BaseConnection


class BaseWriter(ABC):
    def __init__(
        self,
        connection: BaseConnection,
        db_name: str,
        table_name: str,
        if_exists: bool = True,
    ):
        self.connection = connection
        self.db_name = db_name
        self.table_name = table_name
        self.if_exists = if_exists
        
        self._prepare()
    
    @abstractmethod
    def _prepare(self) -> None:
        pass
    
    @abstractmethod
    def start(self, df: DataFrame, **params) -> None:
        pass