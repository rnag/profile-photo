"""
Profile Photo
~~~~~~~~~~~~~

Center + Crop Image to create a Profile Pic or Headshot

Sample Usage:

    >>> from profile_photo import create_headshot
    >>> photo = create_headshot('/path/to/image')
    >>> photo.show()
    >>> # Optional: cache the Rekognition API responses
    >>> photo.save_responses('/path/to/folder')

For full documentation and more advanced usage, please see
<https://profile-photo.readthedocs.io>.

:copyright: (c) 2023 by Ritvik Nag.
:license:MIT, see LICENSE for more details.
"""

__all__ = [
    'create_headshot',
]

import logging

from .main import create_headshot
from .log import LOG

# Set up logging to ``/dev/null`` like a library is supposed to.
# http://docs.python.org/3.3/howto/logging.html#configuring-logging-for-a-library
LOG.addHandler(logging.NullHandler())
