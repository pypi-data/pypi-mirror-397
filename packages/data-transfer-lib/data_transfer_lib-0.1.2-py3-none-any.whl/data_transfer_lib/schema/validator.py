from typing import Dict, Any
from pyspark.sql import DataFrame
from data_transfer_lib.utils.exceptions import SchemaValidationException
from data_transfer_lib.schema.mapper import TypeMapper


class SchemaValidator:

    @staticmethod
    def validate_source_to_spark(source_schema: Dict[str, Any]) -> bool:    
            
        unsupported_types: list[str] = []
        
        for column, pg_type in source_schema.items():
            base_type = pg_type.split('(')[0].strip().lower()
            spark_type = TypeMapper.postgres_to_spark(base_type)
            
            # TODO: do it with flag
            if spark_type == "StringType" and base_type not in TypeMapper.POSTGRES_TO_SPARK:
                unsupported_types.append(f"{column}: {pg_type}")
        
        if unsupported_types:
            error_msg = f"Error:\n Unsupported types detected: {', '.join(unsupported_types)}"
            raise SchemaValidationException(error_msg)
        
        return True
    
    @staticmethod
    def validate_spark_to_target(df_schema: Dict[str, Any], target_schema: Dict[str, Any]) -> bool:
        
        errors: list[str] = []
        warnings: list[str] = []
        
        # Check for missing columns
        df_columns = set(df_schema.keys())
        target_columns = set(target_schema.keys())
        missing_columns = df_columns - target_columns
        if missing_columns:
            errors.append(f"Missing columns: {missing_columns}")
        
        # Check type compatibility for common columns
        for column_name in df_columns & target_columns:
            spark_type = df_schema[column_name]
            target_type = target_schema[column_name]
            
            is_compatible, message = SchemaValidator._check_type_compatibility(
                column_name, spark_type, target_type
            )
            
            if not is_compatible:
                errors.append(message)
            elif message:
                warnings.append(message)
        

        for warning in warnings:
            print(f"Warnings: {warning}")
        
        if errors:
            error_msg = "Uncompatible schemas:\n" + "\n".join(errors)
            print(f"Error: {error_msg}")
            raise SchemaValidationException(error_msg)
        
        print("Validation is succed")
        return True
    
    @staticmethod
    def compare_schemas(source_schema: Dict[str, Any], target_schema: Dict[str, Any]) -> Dict[str, Any]:
        return {}
    
    # TODO: it's easy type checkin, need to be customized
    @staticmethod
    def _check_type_compatibility(column: str, spark_type: str, target_type: str) -> tuple[bool, str]:

        # Check for numeric types compatibility
        spark_numeric_types = {
            "IntegerType", "LongType", "ShortType",
            "DecimalType", "FloatType", "DoubleType"
        }
        is_spark_type_numeric = any(t in spark_type for t in spark_numeric_types)

        target_numeric_types = {
            "Int8", "Int16", "Int32", "Int64",
            "UInt8", "UInt16", "UInt32", "UInt64",
            "Float32", "Float64"
        }
        is_target_type_numeric = any(t in target_type for t in target_numeric_types)
        
        if is_spark_type_numeric and is_target_type_numeric:
            return (True, "")
        
        # Check for string types compatibility
        if "String" in spark_type and "String" in target_type:
            return (True, "")
        
        # Check for date types compatibility
        if "Timestamp" in spark_type and "DateTime" in target_type:
            return (True, "")
        if "Date" in spark_type and "Date" in target_type:
            return (True, "")
        
        # Check for decimal types compatibility
        if "Decimal" in spark_type and "Decimal" in target_type:
            return (True, "")
        
        # Types are not compatible
        return (False, f"Column '{column}': uncompatible types ({spark_type} -> {target_type})")
