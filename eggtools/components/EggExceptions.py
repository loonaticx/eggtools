class EggException(Exception):
    def __init__(self):
        super().__init__(self)


# region EggAttribute Exceptions

class EggAttributeException(EggException):
    def __init__(self):
        super().__init__()


class EggAttributeInvalid(EggAttributeException):
    def __init__(self, attribute_cls, attribute_type):
        super().__init__()
        self.attribute_name = type(attribute_cls).__name__
        self.attribute_type = attribute_type

    def __str__(self):
        return f"Invalid EggAttribute input for {self.attribute_name}: {self.attribute_type}."


# endregion

# region EggMan Exceptions

class EggManException(EggException):

    def __init__(self):
        super().__init__()


class EggImproperArgType(EggManException):
    def __str__(self):
        return f"Wrong usage of parameter. Expected {self.correct} but got {self.incorrect} instead."

    def __init__(self, incorrect_type, correct_type):
        super().__init__()
        self.incorrect = type(incorrect_type)
        self.correct = correct_type


class EggAccessViolation(EggManException):
    """
    Used when improperly accessing EggMan's egg data contents.
    """

    def __str__(self):
        return f"{self.errorMessage}" \
               f"Filename = {self.filename}"

    def __init__(self, egg_data, errorMessage=""):
        super().__init__()
        self.filename = egg_data.getEggFilename()
        self.errorMessage = errorMessage + "\n"

# endregion
