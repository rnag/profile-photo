"""Unit Tests for `profile_photo` package."""
from os import getenv

import pytest
from dataclass_wizard.utils.type_conv import as_bool

from profile_photo import create_headshot
from profile_photo.errors import MissingParams
from ..conftest import images


DEBUG = as_bool(getenv('DEBUG', '0'))


def test_create_headshot_raises_missing_params():
    with pytest.raises(MissingParams) as e:
        _ = create_headshot()

    assert 'parameters [`bucket`, `key`] are required' in str(e.value)


@pytest.mark.parametrize('image', images)
def test_create_headshot_and_show_result(examples, responses, image):
    filepath = examples / image

    create_headshot(
        filepath,
        faces=responses / f'{filepath.stem}_DetectFaces.json',
        labels=responses / f'{filepath.stem}_DetectLabels.json',
        debug=DEBUG,
    )
