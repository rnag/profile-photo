=============
Profile Photo
=============


.. image:: https://img.shields.io/pypi/v/profile-photo.svg
        :target: https://pypi.org/project/profile-photo

.. image:: https://img.shields.io/pypi/pyversions/profile-photo.svg
        :target: https://pypi.org/project/profile-photo

.. image:: https://github.com/rnag/profile-photo/actions/workflows/dev.yml/badge.svg
        :target: https://github.com/rnag/profile-photo/actions/workflows/dev.yml

.. image:: https://readthedocs.org/projects/profile-photo/badge/?version=latest
        :target: https://profile-photo.readthedocs.io/en/latest/?version=latest
        :alt: Documentation Status


.. image:: https://pyup.io/repos/github/rnag/profile-photo/shield.svg
     :target: https://pyup.io/repos/github/rnag/profile-photo/
     :alt: Updates


*Center* + *Crop* Image to create a Profile Pic or Headshot_.

Check out `example images`_ on GitHub for sample use cases and results.

.. _example images: https://github.com/rnag/profile-photo/tree/main/examples
.. _Headshot: https://www.nfi.edu/headshot-photo

Install
-------

.. code-block:: console

    $ pip install profile-photo[all]

The ``[all]`` `extra`_ installs ``boto3``, which is excluded by default - this assumes an AWS environment.

.. _extra: https://packaging.python.org/en/latest/tutorials/installing-packages/#installing-extras

Features
--------

* Exports a helper function, ``create_headshot`` used to create a close-up
  or headshot of the primary face in a photo or image
* Leverages `Amazon Rekognition`_ to detect bounding boxes
  of a person's Face and relevant Labels, such as *Person*
* Exposes helper methods to save the result image (*cropped*) as well as API responses
  to a local folder

.. _Amazon Rekognition: https://docs.aws.amazon.com/rekognition/latest/dg/what-is.html

Usage
-----

Basic usage, with a `sample image`_:

.. code-block:: python3

    from urllib.request import urlopen

    from profile_photo import create_headshot


    # Set the $AWS_PROFILE environment variable instead
    aws_profile = 'my-profile'

    im_url = 'https://raw.githubusercontent.com/rnag/profile-photo/main/examples/woman-2.jpeg'
    im_bytes = urlopen(im_url).read()

    photo = create_headshot(im_bytes, profile=aws_profile)
    photo.show()


An example with a local image, and saving the result image and API responses to a folder:

.. code-block:: python3

    from __future__ import annotations

    from profile_photo import create_headshot


    # customize local file location for API responses
    def get_filename(file_name: str | None, api: str):
        return f'responses/{file_name}_{api}.json'


    photo = create_headshot('/path/to/image')

    # this saves image and API responses to a results/ folder
    # can also be achieved by passing `output_dir` above
    photo.save_all('results', get_response_filename=get_filename)

    # display before-and-after images
    photo.show()

Lastly, an example with an image on S3,
and passing in cached `Rekognition API`_ responses for the image:

.. code-block:: python3

    from pathlib import Path

    from profile_photo import create_headshot


    s3_image_path = Path('path/to/image.jpg')
    responses_dir = Path('./my/responses')

    _photo = create_headshot(bucket='my-bucket',
                             key=str(s3_image_path),
                             profile='my-profile',
                             faces=responses_dir / f'{s3_image_path.stem}_DetectFaces.json',
                             labels=responses_dir / f'{s3_image_path.stem}_DetectLabels.json',
                             debug=True)

.. _sample image: https://raw.githubusercontent.com/rnag/profile-photo/main/examples/woman-2.jpeg
.. _Rekognition API: https://docs.aws.amazon.com/rekognition/latest/APIReference/Welcome.html

How It Works
------------

This library currently makes calls to the `Amazon Rekognition`_ APIs
to detect bounding boxes on a Face and Person in a photo.

It then uses custom, in-house logic to determine the X/Y coordinates
for cropping. This mainly involves "blowing up" or enlarging the Face
bounding box, but then correcting the coordinates as needed by the Person
box. This logic has been fine-tuned based on what I have found provide the
best overall results for generic images (not necessary profile photos).

In the future, other ideas other than *Rekognition* might be considered --
such as existing machine learning approaches or even a solution
with the ``opencv`` library in Python alone.

Future Ideas
------------

* Support background removal with `rembg`_.
* Investigate other (alternate) approaches to *Rekognition* for detecting a face and person in a photo.

.. _rembg: https://pypi.org/project/rembg

Credits
-------

This package was created with Cookiecutter_ and the `rnag/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/cookiecutter/cookiecutter
.. _`rnag/cookiecutter-pypackage`: https://github.com/rnag/cookiecutter-pypackage
