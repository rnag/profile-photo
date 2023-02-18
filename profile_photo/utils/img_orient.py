"""
Rotate an image based on its EXIF orientation flag. All EXIF metadata will be
removed from the transposed image.

Ref: https://www.daveperrett.com/articles/2012/07/28/exif-orientation-handling-is-a-ghetto/
"""
from __future__ import annotations

from dataclasses import MISSING
from io import BytesIO

import cv2
import numpy as np
from PIL import Image
from PIL.Image import Image as PILImage

from ..log import LOG


def get_im_orientation(im_bytes: bytes,
                       orientation: int | None | MISSING = MISSING
                       ) -> (PILImage | None, bool, int | None):
    """
    Check if the image has been rotated, and get the image's orientation.

    Example:
        >>> with open('file.jpg', 'rb') as in_file:
        >>>     im_bytes = in_file.read()
        >>> pil_im, is_rotated, orientation = get_im_orientation(im_bytes)

    Return a three-element tuple of (pil_image, is_rotated, orientation_flag)
    """
    # check if `orientation` is already passed in
    if orientation is MISSING:
        im = Image.open(BytesIO(im_bytes))
        exif = im.getexif()
        orientation: int | None = exif.get(0x0112)
    else:
        im = None

    return im, bool(orientation and orientation != 1), orientation


def get_oriented_im_bytes(file_ext: str,
                          im_bytes: bytes = None,
                          orientation: int | None | MISSING = MISSING) -> (bytes, bool):
    """
    Performs the same operation as `PIL.ImageOps.exif_transpose`_, but using
    the OpenCV library.

    Returns a two-element tuple of (rotated_im_bytes, rotated). If an image
    has an EXIF Orientation tag, return a new image (as bytes) that is
    transposed accordingly. Otherwise, the `rotated` value will be false.

    .. _`PIL.ImageOps.exif_transpose`: https://pillow.readthedocs.io/en/latest/reference/ImageOps.html#PIL.ImageOps.exif_transpose
    """
    _, is_rotated, orientation = get_im_orientation(im_bytes, orientation)

    if not is_rotated:  # No orientation correction is needed on the image.
        return im_bytes, False

    def flip_left_right(im):
        return cv2.flip(im, 1)

    def flip_top_bottom(im):
        return cv2.flip(im, 0)

    def rotate_180(im):
        return cv2.rotate(im, cv2.ROTATE_180)

    def transpose(im):
        return cv2.transpose(im)

    def transverse(im):
        return cv2.rotate(cv2.transpose(im), cv2.ROTATE_180)

    def rotate_90(im):
        return cv2.rotate(im, cv2.ROTATE_90_CLOCKWISE)

    def rotate_90_cc(im):
        return cv2.rotate(im, cv2.ROTATE_90_COUNTERCLOCKWISE)

    method = {
        2: flip_left_right,
        3: rotate_180,
        4: flip_top_bottom,
        5: transpose,
        6: rotate_90,
        7: transverse,
        8: rotate_90_cc,
    }.get(orientation)

    if method is not None:
        LOG.info('Performing orientation correction, orientation=%d, method=%s',
                 orientation, method.__name__)

        # Read in original, un-oriented image (without the EXIF metadata)
        im = cv2.imdecode(np.frombuffer(im_bytes, dtype=np.uint8),
                          cv2.IMREAD_UNCHANGED)

        # Perform orientation correction (transformation) on the image
        im = method(im)

        # Convert an OpenCV image to bytes
        # https://jdhao.github.io/2019/07/06/python_opencv_pil_image_to_bytes/
        is_success, im_buf_arr = cv2.imencode(file_ext, im)

        return im_buf_arr.tobytes(), True

    return im_bytes, False


def resize_ims_and_concat_h(im1: PILImage, im2: PILImage,
                            resample=Image.BICUBIC, resize_big_image=True
                            ) -> PILImage:
    """
    Resize two PIL Images and tile them horizontally.

    Source: https://note.nkmk.me/en/python-pillow-concat-images/

    """
    if im1.height == im2.height:
        _im1 = im1
        _im2 = im2
    elif (((im1.height > im2.height) and resize_big_image) or
          ((im1.height < im2.height) and not resize_big_image)):
        _im1 = im1.resize((int(im1.width * im2.height / im1.height), im2.height), resample=resample)
        _im2 = im2
    else:
        _im1 = im1
        _im2 = im2.resize((int(im2.width * im1.height / im2.height), im1.height), resample=resample)
    dst = Image.new('RGB', (_im1.width + _im2.width, _im1.height))
    dst.paste(_im1, (0, 0))
    dst.paste(_im2, (_im1.width, 0))

    return dst
