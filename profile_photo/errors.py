from __future__ import annotations

from .log import LOG
from .models import Params


class ProfilePhotoError(Exception):
    """
    Base exception class for errors raised by this library.
    """
    ERR_STATUS = 400

    def __init__(self, message, **log_kwargs):
        self.message = message
        self.code = self.__class__.__name__

        super(ProfilePhotoError, self).__init__(self.message)

        if log_kwargs:
            field_vals = [f'{k}={v}' for k, v in log_kwargs.items()]
            message = f'{message.rstrip(".")}. {", ".join(field_vals)}'

        LOG.error('%s: %s', self.code, message)


class FileTooLarge(ProfilePhotoError):

    def __init__(self, size: int, max_size: int):
        msg = (f'The size of image as raw bytes ({size}) is greater '
               f'than {max_size} bytes.\n\n'
               f'Resolution: Upload the image to S3 and pass in '
               f'`bucket` and `key` instead.')

        super(FileTooLarge, self).__init__(msg)


class MissingParams(ProfilePhotoError):
    """Error raised when an input parameter is missing."""

    def __init__(self, *params: Params | str,
                 required_if_missing=None):
        if len(params) > 1:
            params = f'[{str(params)[1:-1]}]'.replace("'", "`")
            msg = f'parameters {params} are required'
        else:
            msg = f'parameter `{params[0]}` is required'

        if required_if_missing:
            reason = f"`{required_if_missing}` is not passed in"
            msg += f' ({reason})'

        super(MissingParams, self).__init__(msg)


class MissingOneOfParams(ProfilePhotoError):
    """Error raised when one of input parameter(s) is missing."""

    def __init__(self, *params: Params | str, required_if_missing=None):
        params = [str(p) for p in params]
        if required_if_missing:
            reason = f"`{required_if_missing}` is not passed in"
            msg = f'{[params]}: one of these inputs is required ({reason})'
        else:
            msg = f'{[params]}: one of these inputs is required'

        super(MissingOneOfParams, self).__init__(msg)
