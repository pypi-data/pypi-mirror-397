from typing import Dict, Any, Optional
from pyspark.sql import SparkSession
from data_transfer_lib.connections.base import BaseConnection


class ClickHouse(BaseConnection):
    def __init__(
        self,
        host: str,
        user: str,
        password: str,
        database: str = "default",
        port: int = 8123,
        spark: Optional[SparkSession] = None
    ):
        super().__init__(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database,
            spark=spark,
        )
    
    def get_jdbc_url(self) -> str:
        return f"jdbc:clickhouse://{self.host}:{self.port}/{self.database}"
    
    def get_connection_properties(self) -> Dict[str, str]:
        return {
            "user": self.user,
            "password": self.password,
            "driver": "com.clickhouse.jdbc.ClickHouseDriver"
        }
    
    def test_connection(self) -> bool:
        return True
    
    def get_table_schema(self, db_name: str, table_name: str) -> Dict[str, Any]:
        schema_query = f"""
            SELECT 
                name,
                type
            FROM system.columns
            WHERE database = '{db_name}' 
                AND table = '{table_name}'
            ORDER BY position
        """

        # TODO: try -> except
        schema_df = (
            self.spark.read
            .format("jdbc")
            .option("url", self.get_jdbc_url())
            .option("query", schema_query)
            .option("user", self.user)
            .option("password", self.password)
            .option("driver", "com.clickhouse.jdbc.ClickHouseDriver")
            .load()
        )

        schema_dict: Dict[str, str] = {}
        for row in schema_df.collect():
            column_name = row['name']
            column_type = row['type']
            schema_dict[column_name] = column_type
        
        return schema_dict
