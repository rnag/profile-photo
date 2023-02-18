from __future__ import annotations

from os.path import splitext

import cv2 as cv
import numpy as np

from .aws.rekognition_models import DetectFacesResp, DetectLabelsResp
from .aws.rekognition_utils import best_fit_coordinates, show_image
from .img_orient import get_oriented_im_bytes, get_im_orientation
from ..models import ProfilePhoto


_DEFAULT_FILE_EXT = '.jpg'


def rotate_im_and_crop(fp: str,
                       faces: DetectFacesResp,
                       labels: DetectLabelsResp | None,
                       file_ext: str | None = None,
                       im_bytes: bytes = None,
                       debug: bool = False,
                       ) -> ProfilePhoto:

    # Get primary face in the photo (might need to be tweaked?)
    face = faces.get_face()

    # Get file extension (.jpg etc.)
    if not file_ext:
        file_ext = splitext(fp)[1] if fp else _DEFAULT_FILE_EXT

    # Get Image Orientation
    _, is_rotated, orientation = get_im_orientation(im_bytes)

    # Correct Image Orientation (If Needed) - Rotate Image
    if is_rotated:
        im_bytes = get_oriented_im_bytes(file_ext, im_bytes, orientation)[0]

    # Read in image data as OpenCV Image
    img_as_np = np.frombuffer(im_bytes, dtype=np.uint8)
    im = cv.imdecode(img_as_np, cv.IMREAD_COLOR)

    # Get bounding box for the Person in the photo
    person_box = labels.get_person_box(face)

    # Get X/Y coordinates for cropping
    coords = best_fit_coordinates(im, face.bounding_box, person_box)

    # Crop the Photo
    #   crop_img = img[y:y+h, x:x+w]
    cropped_im = im[coords.y1:coords.y2, coords.x1:coords.x2]

    # Show cropped image (if debug is enabled)
    if debug:
        show_image('Result', cropped_im)
        cv.waitKey(0)

    # Convert the cropped photo to bytes
    final_im_bytes: bytes = cv.imencode(file_ext, cropped_im)[1].tobytes()

    return ProfilePhoto(
        fp, final_im_bytes, is_rotated, orientation, faces, labels, im_bytes,
    )
