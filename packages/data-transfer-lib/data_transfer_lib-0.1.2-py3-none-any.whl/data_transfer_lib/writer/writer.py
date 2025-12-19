from pyspark.sql import DataFrame
from data_transfer_lib.writer.base import BaseWriter
from data_transfer_lib.connections.base import BaseConnection
from data_transfer_lib.schema.validator import SchemaValidator


class Writer(BaseWriter):
    def __init__(
        self,
        connection: BaseConnection,
        db_name: str,
        table_name: str,
        if_exists: bool = True,
    ):
        self.target_schema = None
        super().__init__(
            connection=connection,
            db_name=db_name,
            table_name=table_name,
            if_exists=if_exists,
        )
    
    def _prepare(self) -> None:
        
        if self.if_exists:
            self.target_schema = self.connection.get_table_schema(
                self.db_name,
                self.table_name
            )
            print(self.target_schema)
        else:
            error_msg = f"{self.db_name}.{self.table_name} table does't exist"
            raise DataTransferException(error_msg)
    
    def start(self, df: DataFrame, **params) -> None:

        df_schema = {}
        for field in df.schema.fields:
            df_schema[field.name] = str(field.dataType)

        try:
            SchemaValidator.validate_spark_to_target(
                df_schema,
                self.target_schema
            )
        except SchemaValidationException as e:
            print(f"Error: {e}")
            raise
        
        try:
            if num_partitions := params.get("num_partitions", None):
                df = df.repartition(num_partitions)
            
            full_table_name = f"{self.db_name}.{self.table_name}"
            
            writer = (
                df.write
                .format("jdbc")
                .option("url", self.connection.get_jdbc_url())
                .option("dbtable", full_table_name)
                .option("user", self.connection.user)
                .option("password", self.connection.password)
                .option("driver", self.connection.get_connection_properties()["driver"])
                .option("batchsize", params.get("batch_size", 10000))
                .mode(params.get("mode", "append"))
            )
            
            writer.save()
            
        except Exception as e:
            raise ConnectionException(f"Couldn't write int table: {e}")
        