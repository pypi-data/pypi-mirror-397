class MempyError(Exception):
    """Exception raised for custom error scenarios.

    Attributes:
        message -- explanation of the error
    """

    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


UNIT_REGISTRY = {
    "hb":   "1/{T}",
    "m":    "{X}",
    "kd":   "1/{T}",
    "b":    "1/{T}/{X}",
    "beta": "",
    "eta":  "1/{T}",
    "eps":  "{X}",
    "w":    "{X}/{X_i}",
}