class CreateException(Exception):
    def __init__(self, message=""):
        self.message = message

    def __str__(self):
        return self.__class__.__name__ + ": " + self.message


class CreateTypeException(CreateException):
    pass


class CreateValueException(CreateException):
    pass


class CreateInvalidVersion(CreateException):
    def __init__(self, config_type: str):
        super().__init__(message=f"Version of {config_type} does not match the current one")
