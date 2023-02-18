from __future__ import annotations

__all__ = ['FillColor',
           'draw_circle',
           'draw_rectangle',
           'draw_box',
           'show_image',
           'best_fit_coordinates']

from enum import Enum
from functools import cached_property

import cv2 as cv
from PIL import Image, ImageDraw

from .rekognition_models import BoundingBox, Landmark, Coordinates
from ...log import LOG


_DEFAULT_OFFSET = 0.17

_SCREEN_WIDTH = _SCREEN_HEIGHT = None


class FillColor(Enum):
    GREEN = '#00d400'
    RED = '#ff0000'
    YELLOW = '#ffff00'
    BLUE = '#0000ff'
    BLACK = '#000000'
    WHITE = '#FFFFFF'

    @cached_property
    def bgr(self):
        """Returns the BGR representation of the color."""
        return hex_to_bgr(self.value)


def get_screen_height_and_width():

    global _SCREEN_HEIGHT
    global _SCREEN_WIDTH

    if _SCREEN_HEIGHT is None or _SCREEN_WIDTH is None:
        import tkinter as tk
        root = tk.Tk()
        _SCREEN_HEIGHT = root.winfo_screenheight()
        _SCREEN_WIDTH = root.winfo_screenwidth()

    return _SCREEN_HEIGHT, _SCREEN_WIDTH


def hex_to_bgr(h: str):
    """
    Converts a hex value (i.e. "#ffff00") to a BGR value (i.e. the inverse of
    RGB).

    Ref: https://stackoverflow.com/a/29643643/10237506
    """
    return tuple(int(h.lstrip('#')[i:i + 2], 16) for i in (4, 2, 0))


def draw_circle(im, landmark: Landmark, color: FillColor = FillColor.YELLOW,
                radius: int = 3, filled=True,
                font_scale=0.4, font_face=cv.FONT_HERSHEY_TRIPLEX,
                text: str = None, text_color: FillColor = FillColor.WHITE):
    """
    Draw a (filled) circle on the image centered around the specified (x, y)
    coordinates for `landmark` and with the specified border `color`
    and radius `radius`.

    Ref: https://www.pyimagesearch.com/2021/01/27/drawing-with-opencv/

    Usage::

        >>> img = cv.imread('path/to/file.jpeg')
        >>> draw_circle(img, data['FaceDetails'][0]['Landmarks'][0], \
                        FillColor.YELLOW, 3, False)

    """

    h, w = im.shape[:2]
    x = round(landmark.x * w)
    y = round(landmark.y * h)

    thickness = cv.FILLED if filled else None

    cv.circle(im, (x, y), radius, color.bgr, thickness)

    if text:
        cv.putText(im, text, (x, y), font_face, font_scale, text_color.bgr)


def best_fit_coordinates(im, face_box: BoundingBox, *boxes: BoundingBox | None,
                         fit=1/3.5,
                         x_offset=_DEFAULT_OFFSET,
                         y_offset=_DEFAULT_OFFSET,
                         constrain_width=True) -> Coordinates:

    # recall: reducing by `offset` will enlarge it
    f_top = face_box.top
    new_top = f_top - y_offset
    # calculate left and right (X) coordinates
    f_left = face_box.left
    f_right = face_box.left + face_box.width

    for box in boxes:

        if not box:
            continue

        # if top is not high enough, adjust

        # if ( L(face) - offset ) is *less* than or close enough to L(box), then
        # we don't do anything - same with right.

        b_top = box.top
        diff = new_top - b_top

        if diff >= 0:
            LOG.info('Enlarging Top, top=%.2f, new_top=%.2f', f_top, b_top)
            face_box.top = f_top = b_top
            new_top = f_top - y_offset
            face_box.height += diff + y_offset

        b_left = box.left
        b_right = b_left + box.width

        area_left = abs(f_left - b_left)
        area_right = abs(b_right - f_right)

        threshold_left = b_left + fit * area_left
        threshold_right = b_right - fit * area_right

        needs_fit = (f_left - x_offset) > threshold_left and (f_right + x_offset) < threshold_right

        # now left and right

        if needs_fit:
            offset_l = f_left - threshold_left
            offset_r = threshold_right - f_right
            x_offset = max(offset_l, offset_r)
            LOG.info('Enlarging Width, new_offset=%.3f', x_offset)

        if constrain_width:
            out_of_box = b_left > f_left - x_offset and b_right < f_right + x_offset
            if out_of_box:
                LOG.info('Constraining Width for Face')
                face_box.left = b_left + x_offset
                face_box.width = box.width - 2 * x_offset

    face_coords = Coordinates.from_box(im, face_box, x_offset, y_offset)

    return face_coords


def draw_rectangle(im, coords_or_box: Coordinates | BoundingBox,
                   color: FillColor = FillColor.GREEN,
                   offset=0,
                   y_offset=0,
                   line_width=3):
    """
    Draw a bounding box on the image at the specified coordinates `box` and with
    the specified border `color` and `line_width`.

    An optional `offset` can be provided to enhance or "zoom out" on the box
    coordinates.

    Ref: https://stackoverflow.com/questions/23720875/how-to-draw-a-rectangle-around-a-region-of-interest-in-python

    Usage::

        >>> img = cv.imread('path/to/file.jpeg')
        >>> draw_rectangle(img, data['FaceDetails'][0]['BoundingBox'], FillColor.YELLOW)

    """

    c = Coordinates.from_box(im, coords_or_box, offset, y_offset) \
        if isinstance(coords_or_box, BoundingBox) else coords_or_box

    cv.rectangle(
        im,
        (c.x1, c.y1),
        (c.x2, c.y2),
        color.bgr,
        line_width,
    )


def draw_box(image: Image, box: BoundingBox,
             color: FillColor = FillColor.GREEN, line_width=3,
             offset=0):
    """
    Draw a bounding box on the image at the specified coordinates `box` and with
    the specified border `color` and `line_width`. An optional `offset` can be
    provided to change box coordinates. For example, an offset of
    `line_width + line_width` can be used to create an "inner" bounding box.

    Displays the image after the box has been drawn.

    Ref: https://docs.aws.amazon.com/rekognition/latest/dg/images-displaying-bounding-boxes.html

    Usage::

        >>> im = Image.open('path/to/file.jpeg')
        >>> draw_box(im, data['FaceDetails'][0]['BoundingBox'], FillColor.YELLOW)

    """
    draw = ImageDraw.Draw(image)
    im_width, im_height = image.size

    # draw a colored bounding box
    left = im_width * box.left
    top = im_height * box.top
    width = im_width * box.width
    height = im_height * box.height

    points = (
        (left + offset, top + offset),
        (left + width - offset, top + offset),
        (left + (width - offset), (top - offset) + height),
        (left + offset, top + (height - offset)),
        (left + offset, top + offset)
    )

    draw.line(points, fill=color.value, width=line_width)

    image.show()


def show_image(name, img, area=0.5, window_h=0, window_w=0):
    """
    Displays an image after resizing it to the specified dimensions, while
    also ensuring that we retain its aspect ratio.

    Credits: https://stackoverflow.com/a/67718163/10237506
    """

    import math

    h, w = img.shape[:2]

    screen_h, screen_w = get_screen_height_and_width()
    # import tkinter as tk
    # root = tk.Tk()
    # screen_h = root.winfo_screenheight()
    # screen_w = root.winfo_screenwidth()

    if area:
        vector = math.sqrt(area)
        window_h = screen_h * vector
        window_w = screen_w * vector

    if h > window_h or w > window_w:
        if h / window_h >= w / window_w:
            multiplier = window_h / h
        else:
            multiplier = window_w / w
        img = cv.resize(img, (0, 0), fx=multiplier, fy=multiplier)

    cv.imshow(name, img)
