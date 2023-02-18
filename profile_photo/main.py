"""Main module."""
from __future__ import annotations

from os import stat, PathLike
from pathlib import Path
from sys import getsizeof

from .helpers import Util
from .models import Params, ProfilePhoto
from .utils.aws.rekognition import Rekognition
from .utils.aws.rekognition_models import DetectFacesResp, DetectLabelsResp
from .utils.aws.s3 import S3Helper
from .utils.create_headshot import rotate_im_and_crop
from .utils.json_util import load_to_model


def create_headshot(
    filepath_or_bytes: PathLike[str] | PathLike[bytes] | str | bytes | None = None,
    *,
    file_ext: str | None = None,
    faces: DetectFacesResp | Path | dict | str | None = None,
    labels: DetectLabelsResp | Path | dict | str | None = None,
    region: str = 'us-east-1',
    profile: str | None = None,
    bucket: str | None = None,
    key: str | None = None,
    debug: bool = False,
    output_dir: PathLike[str] | PathLike[bytes] | str = None,
) -> ProfilePhoto:

    futures = {}

    # do we need to make a Rekognition API call?
    call_rekognition_api = not (faces and labels)

    # image file path or bytes is passed in
    if filepath_or_bytes:

        # image data (as bytes) is passed in
        if isinstance(filepath_or_bytes, bytes):
            # filepath is same as key
            filepath = key
            # image bytes is known
            im_bytes = filepath_or_bytes
            # do we need to make a Rekognition API call?
            if call_rekognition_api and not (bucket and key):
                # validate that image size is < 5MB
                im_len = getsizeof(im_bytes)
                Util.validate_file_len(im_len)

        # local filepath is passed in
        else:
            # filepath is known
            filepath = filepath_or_bytes
            if call_rekognition_api and not (bucket and key):
                # validate that image size is < 5MB
                im_len = stat(filepath).st_size
                Util.validate_file_len(im_len)
            # read image data from local file
            with open(filepath, 'rb') as f:
                im_bytes = f.read()

    # neither file path nor image data is passed in - read in image from S3
    else:
        # filepath is same as key
        filepath = key
        # image bytes is not yet resolved
        im_bytes = None
        _param = Params.FILEPATH_OR_BYTES
        # check that `bucket` and `key` is passed in
        Util.validate_params(_param, bucket=bucket, key=key)
        # retrieve image from S3 (runs in background)
        futures[_param] = Util.pool.submit(
            S3Helper(region, profile).get_object_bytes,
            bucket, key,
        )

    if call_rekognition_api:
        # Is a DetectFaces API Response already passed in?
        if not faces:
            _param = Params.FACES
            # call DetectFaces API on the image (runs in background)
            futures[_param] = Util.pool.submit(
                Rekognition(region, profile, init_client=True).detect_faces,
                bucket, key, im_bytes, debug,
            )
        # Is a DetectLabels API Response already passed in?
        if not labels:
            _param = Params.LABELS
            # call DetectLabels API on the image (runs in background)
            futures[_param] = Util.pool.submit(
                Rekognition(region, profile, init_client=True).detect_labels,
                bucket, key, im_bytes, debug,
            )

    # join any futures
    if futures:
        # resolve GetFaces API response
        _fut = futures.get(Params.FACES)
        if _fut:
            faces = _fut.result()
        # resolve GetLabels API response
        _fut = futures.get(Params.LABELS)
        if _fut:
            labels = _fut.result()
        # resolve image data from S3
        _fut = futures.get(Params.FILEPATH_OR_BYTES)
        if _fut:
            im_bytes = _fut.result()

    # transform or load the API responses passed in (if needed)
    faces = load_to_model(DetectFacesResp, faces, Params.FACES)
    labels = load_to_model(DetectLabelsResp, labels, Params.LABELS)

    # rotate & crop the photo
    photo = rotate_im_and_crop(
        filepath, faces, labels, file_ext, im_bytes, debug)

    # save outputs to a local drive (if needed)
    if output_dir:
        if call_rekognition_api:
            photo.save_all(output_dir)
        else:
            photo.save_image(output_dir)

    # return the photo as headshot
    return photo
