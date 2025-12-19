class DataTransferException(Exception):
    pass


class ConnectionException(DataTransferException):
    pass


class SchemaValidationException(DataTransferException):
    pass


class TypeMappingException(DataTransferException):
    pass