class YamlOOPException(Exception):
    """Base exception for all yaml_oop-specific errors."""

    def __init__(self, message: str):
        super().__init__(message)


class CircularInheritanceException(YamlOOPException):
    def __init__(self, message):
        super().__init__(message)


class KeySealedException(YamlOOPException):
    def __init__(self, message):
        super().__init__(message)


class ConflictingDeclarationException(YamlOOPException):
    def __init__(self, message):
        super().__init__(message)


class NoOverrideException(YamlOOPException):
    def __init__(self, message):
        super().__init__(message)


class InvalidVariableException(YamlOOPException):
    def __init__(self, message):
        super().__init__(message)


# TO DO
class AmbiguousVariableException(YamlOOPException):
    def __init__(self, message):
        super().__init__(message)


class InvalidInstantiationException(YamlOOPException):
    def __init__(self, message):
        super().__init__(message)


class InvalidDeclarationException(YamlOOPException):
    def __init__(self, message):
        super().__init__(message)
