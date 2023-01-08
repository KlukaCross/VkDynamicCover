import typing


class CreateException(Exception):
    def __init__(self, message=""):
        self.message = message

    def __str__(self):
        return self.__class__.__name__ + ": " + self.message


class CreateTypeException(CreateException):
    def __init__(self, name_value: str, needed_type: typing.Union[list, any], got_type: any):
        if isinstance(needed_type, list):
            super().__init__ (f"{name_value} must be one of the {needed_type}, got {got_type}")
        else:
            super().__init__(f"{name_value} must be {needed_type}, got {got_type}")


class CreateValueException(CreateException):
    def __init__(self, name_value: str, needed_value: typing.Union[list, any], got_value: any):
        if isinstance(needed_value, list):
            super().__init__ (f"{name_value} must be one of the {needed_value}, got {got_value}")
        else:
            super().__init__(f"{name_value} must be {needed_value}, got {got_value}")


class CreateInvalidVersion(CreateException):
    def __init__(self, config_type: str):
        super().__init__(message=f"Version of {config_type} does not match the current one")
