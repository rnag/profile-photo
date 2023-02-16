"""
Profile Photo
~~~~~~~~~~~~~

Crop Image to create Profile Pic or Headshot

Sample Usage:

    >>> import profile_photo

For full documentation and more advanced usage, please see
<https://profile-photo.readthedocs.io>.

:copyright: (c) 2023 by Ritvik Nag.
:license:MIT, see LICENSE for more details.
"""

__all__ = [

]

import logging


# Set up logging to ``/dev/null`` like a library is supposed to.
# http://docs.python.org/3.3/howto/logging.html#configuring-logging-for-a-library
logging.getLogger('profile_photo').addHandler(logging.NullHandler())
