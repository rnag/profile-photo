from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from functools import cached_property
from io import BytesIO
from os import PathLike
from os.path import splitext, basename
from pathlib import Path
from typing import TYPE_CHECKING

from PIL import Image
from PIL.Image import Image as PILImage

from .utils.aws.rekognition_models import DetectLabelsResp, DetectFacesResp
from .utils.img_orient import resize_ims_and_concat_h


if TYPE_CHECKING:
    from typing import Protocol

    class GetImFileName(Protocol):
        def __call__(self, file_stem: str, file_ext: str) -> PathLike[str] | str:
            ...

    class GetResponseFileName(Protocol):
        def __call__(self, file_name: str, api: str) -> PathLike[str] | str:
            ...


def _get_im_filename(file_stem: str, file_ext: str) -> PathLike[str] | str:
    return f'{file_stem}-out{file_ext}'


def _get_response_filename(file_name: str, api: str) -> PathLike[str] | str:
    return f'{file_name}_{api}_resp.json'


@dataclass
class ProfilePhoto:
    filepath: str | None
    im_bytes: bytes
    is_rotated: bool
    orientation: int | None
    faces: DetectFacesResp
    labels: DetectLabelsResp

    # PRIVATE
    _original_im_bytes: bytes = field(repr=False)

    # default filename
    _DEFAULT_FILENAME = 'output.jpg'

    @cached_property
    def image(self) -> PILImage:
        """Returns the final photo as a PIL Image."""
        return Image.open(BytesIO(self.im_bytes))

    @cached_property
    def side_by_side_image(self) -> PILImage:
        """
        Returns a horizontally concatenated photo (before and after)
        as a PIL Image.
        """
        orig_im = Image.open(BytesIO(self._original_im_bytes))
        return resize_ims_and_concat_h(orig_im, self.image)

    def show(self, side_by_side=True, title='Profile Photo'):
        """
        Show the Profile Photo (as a PIL Image) in a new window.

        If `side_by_side` is True (the default), then also show
        the original image on the left.

        """
        im = self.side_by_side_image if side_by_side else self.image
        im.show(title)

    def save_all(self, folder: Path | str | None = None,
                 get_im_filename: GetImFileName = _get_im_filename,
                 get_response_filename: GetResponseFileName = _get_response_filename):
        """Save both the output image and API responses to a local folder."""
        path = self._path(folder)

        self.save_image(path, get_im_filename)
        self.save_responses(path, get_response_filename)

    def save_image(self, folder: Path | str | None = None,
                   get_filename: GetImFileName = _get_im_filename):
        """Save the output image to a local folder."""
        folder = self._path(folder)
        folder.mkdir(exist_ok=True)

        filename, ext = splitext(fp if (fp := self.filepath) else self._DEFAULT_FILENAME)
        out_filename = get_filename(basename(filename), ext)

        self.image.save(folder / out_filename)

    def save_responses(self, folder: Path | str | None = None,
                       get_filename: GetResponseFileName = _get_response_filename):
        """
        Save (or cache) Rekognition API responses -- from the Detect Faces API
        and Detect Labels API -- as separate JSON files under a folder or path.

        """
        folder = self._path(folder)

        fp = self.filepath
        f_name = Path(fp if fp else self._DEFAULT_FILENAME).stem

        for (api, resp) in (('DetectFaces', self.faces),
                            ('DetectLabels', self.labels)):
            fpath = folder / get_filename(f_name, api)

            # ensure that output folder exists
            if (parent := fpath.parent) != '.':
                parent.mkdir(parents=True, exist_ok=True)

            with open(fpath, 'w') as f:
                f.write(resp.to_json())

    def _path(self, folder: Path | str | None):
        if isinstance(folder, Path):
            return folder

        if folder:
            return Path(folder)

        fp = self.filepath

        if not fp:
            from .errors import MissingOneOfParams
            raise MissingOneOfParams('filepath_or_bytes', required_if_missing='folder')

        return Path(fp).parent


class StrEnum(str, Enum):

    @classmethod
    def values(cls):
        """Returns an iterable of all values in the `Enum` subclass."""
        return (str(v) for v in cls.__members__.values())

    def __str__(self) -> str:
        return str.__str__(self)


class Params(StrEnum):
    """Required Params -- one of FILEPATH_OR_BYTES or {FACES, LABELS}."""
    FILEPATH_OR_BYTES = 'filepath_or_bytes'
    FACES = 'faces'
    LABELS = 'labels'
