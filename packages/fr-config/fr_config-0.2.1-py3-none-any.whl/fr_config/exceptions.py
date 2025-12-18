# Copyright (C) 2024 Floating Rock Studio Ltd
class FRConfigException(Exception):
    pass


class DataValidationException(FRConfigException):
    pass


class SchemaValidationException(FRConfigException):
    pass
