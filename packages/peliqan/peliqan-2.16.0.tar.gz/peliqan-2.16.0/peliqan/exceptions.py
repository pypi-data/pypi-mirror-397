class PeliqanClientException(Exception):
    """
    Base exception raised by the Peliqan module.
    """

    def __init__(self, message, code=None, error_dict=None, *args, **kwargs):
        self.message = message
        self.code = code
        self.error_dict = error_dict

    @property
    def error(self):
        return {
            'code': self.code,
            'message': self.message,
            'error_dict': self.error_dict,
        }


class OperationNotSupported(PeliqanClientException):
    """
        Raise this when an operation is not support by the client.
    """


class PeliqanJsonSerializerException(PeliqanClientException):
    """
        Raise this when a json encoding fails for a data structure.
    """
