=====
Usage
=====

First, ensure that your ``$AWS_PROFILE`` environment is correctly set up::

    export AWS_PROFILE='my-profile'

To use Profile Photo in a project::

    from profile_photo import create_headshot


    photo = create_headshot('/path/to/image')

    # Display the before-and-after images
    photo.show()

    # Optional: cache the Rekognition API responses
    photo.save_responses('/path/to/folder')
