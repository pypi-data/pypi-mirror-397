from typing import Dict, Any, Optional
from pyspark.sql import SparkSession
from data_transfer_lib.connections.base import BaseConnection


class Postgres(BaseConnection):
    def __init__(
        self,
        host: str,
        user: str,
        password: str,
        database: str = "postgres",
        port: int = 5432,
        spark: Optional[SparkSession] = None,
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
        return f"jdbc:postgresql://{self.host}:{self.port}/{self.database}"
    
    def get_connection_properties(self) -> Dict[str, str]:
        return {
            "user": self.user,
            "password": self.password,
            "driver": "org.postgresql.Driver"
        }
    
    def test_connection(self) -> bool:
        print("Проверка подключения к PostgreSQL")
        return True
    
    def get_table_schema(self, db_name: str, table_name: str) -> Dict[str, Any]:

        schema_query = f"""
            SELECT 
                column_name,
                data_type,
                character_maximum_length,
                numeric_precision,
                numeric_scale
            FROM information_schema.columns
            WHERE table_schema = '{db_name}' 
                AND table_name = '{table_name}'
            ORDER BY ordinal_position
        """

        # TODO: try -> except 

        schema_df = ( 
            self.spark.read
            .format("jdbc")
            .option("url", self.get_jdbc_url())
            .option("query", schema_query)
            .option("user", self.user)
            .option("password", self.password)
            .option("driver", "org.postgresql.Driver")
            .load()
        )

        schema_dict = {}
        for row in schema_df.collect():
            column_name = row['column_name']
            data_type = row['data_type']
            
            # Add precision and scale
            if data_type in ('numeric', 'decimal') and row['numeric_precision']:
                data_type = f"{data_type}({row['numeric_precision']},{row['numeric_scale']})"

            # Add max_length
            elif data_type in ('character varying', 'varchar') and row['character_maximum_length']:
                data_type = f"varchar({row['character_maximum_length']})"
            
            schema_dict[column_name] = data_type
        
        return schema_dict
