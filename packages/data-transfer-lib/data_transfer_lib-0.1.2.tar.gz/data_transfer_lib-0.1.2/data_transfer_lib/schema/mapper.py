from typing import Dict, Any
from pyspark.sql.types import DataType


class TypeMapper:
    POSTGRES_TO_SPARK = {
        # Boolean
        "boolean": "BooleanType",
        "bool": "BooleanType",
        
        # Integer types
        "smallint": "ShortType",
        "int2": "ShortType",
        "smallserial": "ShortType",
        "serial2": "ShortType",
        
        "integer": "IntegerType",
        "int": "IntegerType",
        "int4": "IntegerType",
        "serial": "IntegerType",
        "serial4": "IntegerType",
        
        "bigint": "LongType",
        "int8": "LongType",
        "bigserial": "LongType",
        "serial8": "LongType",
        
        # Floating point
        "real": "FloatType",
        "float4": "FloatType",
        "double precision": "DoubleType",
        "float8": "DoubleType",
        # float и float(p) обрабатываются отдельно
        
        # Numeric/Decimal
        "numeric": "DecimalType",
        "decimal": "DecimalType",
        
        # String types
        "character varying": "StringType",  # varchar
        "varchar": "StringType",
        "character": "StringType",  # char
        "char": "StringType",
        "bpchar": "StringType",
        "text": "StringType",
        
        # Binary
        "bytea": "BinaryType",
        
        # Date/Time
        "date": "DateType",
        "timestamp": "TimestampType",
        "timestamp without time zone": "TimestampType",
        "timestamp with time zone": "TimestampType",
        "timestamptz": "TimestampType",
        "time": "TimestampType",
        "time without time zone": "TimestampType",
        "time with time zone": "TimestampType",
        "timetz": "TimestampType",
        
        # Interval
        "interval": "StringType",
        
        # Monetary
        "money": "StringType",
        
        # Network Address Types
        "inet": "StringType",
        "cidr": "StringType",
        "macaddr": "StringType",
        "macaddr8": "StringType",
        
        # Geometric Types
        "point": "StringType",
        "line": "StringType",
        "lseg": "StringType",
        "box": "StringType",
        "path": "StringType",
        "polygon": "StringType",
        "circle": "StringType",
        
        # Log Sequence Number
        "pg_lsn": "StringType",
        
        # Bit types handled separately (bit(1) -> BooleanType, bit(>1) -> BinaryType)
        
        # Text Search Types
        "tsvector": "StringType",
        "tsquery": "StringType",
        
        # UUID
        "uuid": "StringType",
        
        # XML
        "xml": "StringType",
        
        # JSON
        "json": "StringType",
        "jsonb": "StringType",
        
        # Range Types
        "int4range": "StringType",
        "int8range": "StringType",
        "numrange": "StringType",
        "tsrange": "StringType",
        "tstzrange": "StringType",
        "daterange": "StringType",
        
        # Object Identifier Types
        "oid": "DecimalType",
        "regproc": "StringType",
        "regprocedure": "StringType",
        "regoper": "StringType",
        "regoperator": "StringType",
        "regclass": "StringType",
        "regtype": "StringType",
        "regrole": "StringType",
        "regnamespace": "StringType",
        "regconfig": "StringType",
        "regdictionary": "StringType",
        
        # Pseudo types
        "void": "NullType",
        
        # ENUM types map to StringType
        # Array types map to ArrayType
        # Composite types map to StringType
    }
    
    SPARK_TO_CLICKHOUSE = {
        "IntegerType": "Int32",
        "LongType": "Int64",
        "ShortType": "Int16",
        "DecimalType": "Decimal",
        "FloatType": "Float32",
        "DoubleType": "Float64",
        "StringType": "String",
        "TimestampType": "DateTime",
        "DateType": "Date",
        "BooleanType": "UInt8",
    }

    
    @classmethod
    def postgres_to_spark(cls, pg_type: str) -> str:
        base_type, params = cls._parse_pg_type(pg_type)
        
        # float(p) - depends on precision
        if base_type == "float":
            if params and len(params) > 0:
                p = int(params[0])
                if 1 <= p <= 24:
                    return "FloatType"
                elif 25 <= p <= 53:
                    return "DoubleType"
            return "DoubleType"
        
        # bit types
        if base_type == "bit":
            if params and len(params) > 0:
                n = int(params[0])
                if n == 1:
                    return "BooleanType"
                else:
                    return "BinaryType"
            else:
                # bit(1)
                return "BooleanType"
        
        if base_type == "bit varying" or base_type == "varbit":
            return "BinaryType"
        
        if base_type in ("character varying", "varchar") and params:
            return f"VarcharType({params[0]})"
        
        if base_type in ("character", "char") and params:
            return f"CharType({params[0]})"
        
        # numeric(p, s) / decimal(p, s)
        if base_type in ("numeric", "decimal"):
            if params and len(params) >= 1:
                p = int(params[0])
                s = int(params[1]) if len(params) > 1 else 0
                
                # PostgreSQL 15+: if s < 0
                if s < 0:
                    adjusted_p = min(p - s, 38)
                    return f"DecimalType({adjusted_p}, 0)"
                
                # If p > 38, the fraction part will be truncated if exceeded
                if p > 38:
                    # TODO: if any value of this column have an actual precision greater 38
                    # will fail with NUMERIC_VALUE_OUT_OF_RANGE.WITHOUT_SUGGESTION error.
                    return f"DecimalType(38, {min(s, 38)})"
                
                return f"DecimalType({p}, {s})"
            else:
                return "DecimalType(38, 0)"
        
        if base_type == "oid":
            return "DecimalType(20, 0)"
        
        if base_type.endswith("[]"):
            element_type = base_type[:-2]
            element_spark_type = cls.postgres_to_spark(element_type)
            return f"ArrayType({element_spark_type})"
        
        # Other mapping - OK
        spark_type = cls.POSTGRES_TO_SPARK.get(base_type.lower())
        
        if spark_type:
            return spark_type
        
        # TODO: Exception for inknown type of PostgreSQL -> now to StringType
        return "StringType"
    
    @staticmethod
    def _parse_pg_type(pg_type: str) -> tuple:
        """
        Args:
            pg_type: For example "varchar(100)", "numeric(10,2)", "bit(5)"
        Returns:
            (base_type, [params]) - For example ("varchar", ["100"]), ("numeric", ["10", "2"])
        """
        pg_type = pg_type.strip().lower()
        
        if "(" in pg_type and ")" in pg_type:
            base_type = pg_type[:pg_type.index("(")].strip()
            params_str = pg_type[pg_type.index("(") + 1:pg_type.rindex(")")].strip()
            params = [p.strip() for p in params_str.split(",")]
            return base_type, params
        else:
            return pg_type, []
    
    @classmethod
    def spark_to_clickhouse(cls, spark_type: str) -> str:
        return cls.SPARK_TO_CLICKHOUSE.get(spark_type, "String")
    
    @classmethod
    def validate_mapping(cls, source_type: str, target_type: str) -> bool:
        return True
