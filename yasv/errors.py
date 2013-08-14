class InvalidCleanedDataError(Exception):
    def __init__(self, message='', field_name='', field_label=''):
        self.message = message
        self.field_name = field_name
        self.field_label = field_label


class ValidationError(Exception):
    """ Raised when a validator fails to validate its input.
    """
    def __init__(self):
        self.error_response = {}
