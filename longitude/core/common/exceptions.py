class LongitudeBaseException(Exception):
    pass


class LongitudeRetriesExceeded(LongitudeBaseException):
    pass


class LongitudeAppNotReady(LongitudeBaseException):
    pass


class LongitudeQueryCannotBeExecutedException(LongitudeBaseException):
    pass


class LongitudeWrongQueryException(LongitudeBaseException):
    pass


class LongitudeConfigError(LongitudeBaseException):
    pass


class LongitudeWrongHTTPCommand(LongitudeBaseException):
    pass
