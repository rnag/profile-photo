"""Integration Tests for `profile_photo` package."""

import pytest

from profile_photo import create_headshot
from ..conftest import images


@pytest.mark.parametrize('image', images)
def test_create_headshot_and_save_all(examples, responses, image):

    # Set the $AWS_PROFILE environment variable instead
    profile = None

    photo = create_headshot(examples / image, profile=profile)

    def get_filename(filename: str | None, api: str):
        return responses / (f'{filename}_{api}.json' if filename else f'{api}_resp.json')

    # can also be achieved by passing `output_dir` above
    photo.save_all(examples, get_filename)


@pytest.mark.parametrize('image', images)
def test_create_headshot_and_show_side_by_side(examples, responses, image):
    filepath = examples / image

    photo = create_headshot(
        filepath,
        faces=responses / f'{filepath.stem}_DetectFaces.json',
        labels=responses / f'{filepath.stem}_DetectLabels.json',
    )

    photo.show()


def test_with_s3_object():
    photo = create_headshot(bucket='my-bucket',
                            key='/my/image.jpeg',
                            profile='my-profile',
                            debug=True)
