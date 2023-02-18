from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor

from dataclass_wizard.decorators import cached_class_property

from .errors import FileTooLarge, MissingParams
from .models import Params


class Util:
    """Helper Utilities."""
    pool: ThreadPoolExecutor
    max_threads = 3

    # noinspection PyMethodParameters
    @cached_class_property
    def pool(cls):
        return ThreadPoolExecutor(max_workers=cls.max_threads)

    @staticmethod
    def validate_file_len(size: int, _max_size=5_000_000):
        """Validate file length is < 5 MB.

        The maximum images size as raw bytes passed in as parameter to
        the Rekognition API is 5 MB.

        See: https://docs.aws.amazon.com/rekognition/latest/dg/limits.html#quotas

        """
        if size > _max_size:
            raise FileTooLarge(size, _max_size) from None

    @staticmethod
    def validate_params(required_if_missing: Params | None = None, **params):
        """Validate required parameters are passed in."""
        invalid: list | None = None

        for p in params:
            if not params[p]:
                if invalid:
                    invalid.append(p)
                else:
                    invalid = [p]

        if invalid:
            raise MissingParams(*invalid, required_if_missing=required_if_missing) from None
