class EggException(Exception):
    def __init__(self):
        super().__init__(self)


class EggImproperArgType(EggException):
    def __str__(self):
        return f"Wrong usage of parameter. Expected {self.correct} but got {self.incorrect} instead."

    def __init__(self, incorrect_type, correct_type):
        super().__init__()
        self.incorrect = type(incorrect_type)
        self.correct = correct_type


class EggAccessViolation(EggException):
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
