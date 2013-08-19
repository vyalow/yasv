class ValidationError(Exception):
    """ Raised when a validator fails to validate its input.
    """
    def __init__(self):
        self.error_response = {}
