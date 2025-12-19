from pyspark.sql import DataFrame
from data_transfer_lib.reader.base import BaseReader
from data_transfer_lib.connections.base import BaseConnection
from data_transfer_lib.schema.validator import SchemaValidator

class Reader(BaseReader):
    def __init__(
        self,
        connection: BaseConnection,
        db_name: str,
        table_name: str,
    ):
        self.source_schema = None
        super().__init__(
            connection=connection,
            db_name=db_name,
            table_name=table_name,
        )
    
    def _prepare(self) -> None:
        print("prepare")
        
        self.source_schema = self.connection.get_table_schema(
            self.db_name,
            self.table_name
        )
        
        SchemaValidator.validate_source_to_spark(self.source_schema)
    
    def start(self) -> DataFrame:

        table_name = f"{self.db_name}.{self.table_name}"
        
        reader = (
            self.connection
            .spark.read
            .format("jdbc")
            .option("url", self.connection.get_jdbc_url())
            .option("dbtable", table_name)
            .option("user", self.connection.user)
            .option("password", self.connection.password)
            .option("driver", self.connection.get_connection_properties()["driver"])
        )
        df = reader.load()
        return df
