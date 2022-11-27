class CreateException(Exception):
    def __init__(self, message=""):
        self.message = message

    def __str__(self):
        return self.__class__.__name__ + ": " + self.message


class CreateTypeException(CreateException):
    pass


class CreateValueException(CreateException):
    pass
