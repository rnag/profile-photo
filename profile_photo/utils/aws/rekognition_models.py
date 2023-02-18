from __future__ import annotations

__all__ = [
    'Coordinates',
    'DetectLabelsResp',
    'DetectFacesResp',
    'RecognizeCelebritiesResp',
    'CompareFacesResp',
    'Face',
    'Label',
    'FaceDetail',
    'BoundingBox',
    'Landmark'
]

from dataclasses import dataclass
from functools import cached_property
from typing import List, Literal, Optional

from dataclass_wizard import JSONWizard

from ..dict_helper import DictWithLowerStore


ImageOrientation = Literal['ROTATE_0', 'ROTATE_90', 'ROTATE_180', 'ROTATE_270']


@dataclass
class Coordinates:
    """
    Coordinates dataclass.

    Can be visualized using this diagram:

          x1,y1 -----------------
          |                     |
          |                     |
          |                     |
          |                     |
          |                     |
          ------------------ x2,y2

    """
    x1: int
    y1: int
    x2: int
    y2: int

    @classmethod
    def from_box(cls, im, box: BoundingBox, offset=0, y_offset=0):
        im_height, im_width = im.shape[:2]

        # draw a colored bounding box
        x1_orig = im_width * box.left
        y1_orig = im_height * box.top
        width = im_width * box.width
        height = im_height * box.height
        # calculate `offset` as relative to width and height (x and y) dimensions
        offset_x = im_width * offset
        offset_y = im_height * y_offset

        # Assume in the top-left corner of the image we have (x=0, y=0), and at the
        # bottom-right, we have (x=height, y=width).
        #
        # Assumption here is the offset will magnify the bounding box, so it will
        # *increase* in size. The result coordinates after applying the offset is
        # indicated by (x1T, y1T) and (x2T,y2T) in the diagram below.
        #
        # (0, 0)
        # ...
        #   \
        #    \
        #     x1T,y1T ------------
        #     |                  |
        #     |   x1,y1 ------   |
        #     |   |          |   |
        #     |   |          |   |
        #     |   |          |   |
        #     |   --------x2,y2  |
        #     |                  |
        #     ---------------x2T,y2T
        #                        \
        #                         \
        #                         ...
        #                         (x_max, y_max)
        #                           -or-
        #                         (height, width)
        #
        # Hence, from above, note that we want to reduce the value of both (x1, y1)
        # and increase both (x2, y2). That will get us desired coordinates with offset
        # applied as expected.

        x1, y1 = round(x1_orig - offset_x), round(y1_orig - offset_y)
        x2, y2 = round(x1_orig + (width + offset_x)), round((y1_orig + offset_y) + height)

        return cls(max(x1, 0), max(y1, 0), min(x2, im_width), min(y2, im_height))


@dataclass
class RecognizeCelebritiesResp(JSONWizard):
    """
    Response from the Rekognition RecognizeCelebrities API

    """
    celebrity_faces: List['CelebrityFace']
    unrecognized_faces: List['Face']
    orientation_correction: ImageOrientation = 'ROTATE_0'


@dataclass
class CelebrityFace:
    """
    CelebrityFace dataclass

    """
    urls: List[str]
    name: str
    id: str
    face: 'Face'
    match_confidence: float


@dataclass
class Face:
    """
    Face dataclass

    """
    bounding_box: 'BoundingBox'
    confidence: float
    landmarks: List['Landmark']
    pose: 'Pose'
    quality: 'Quality'


@dataclass
class DetectLabelsResp(JSONWizard):
    """
    Response from Rekognition DetectLabels API

    """
    labels: List['Label']

    # Technically provided in response, but we don't need this.
    # label_model_version: Union[float, str]

    @cached_property
    def label_name_to_value(self) -> DictWithLowerStore[str, 'Label']:
        """
        Return a case-insensitive mapping of label name to label.
        """
        return DictWithLowerStore(
            {label.name: label for label in self.labels})

    def get_person_box(self, face: FaceDetail | None) -> BoundingBox | None:
        """
        Get the bounding box for the 'Person' label.

        If there are multiple instances of a 'Person', then the argument
        for `face` helps pinpoint a matching person.

        """
        labels = self.label_name_to_value
        person = labels.get('person')

        if people := person.instances:

            # if there's only one person in the image
            if len(people) == 1:
                first = people[0]
                return first.bounding_box

            # if there's multiple people in the image, find the
            # person instance which wraps the input face box

            if face is None:
                return None

            face_box = face.bounding_box
            face_left = face_box.left
            face_right = face_left + face_box.width

            for person in people:
                person_box = person.bounding_box
                person_left = person_box.left
                person_right = person_left + person_box.width

                if person_left <= face_left and person_right >= face_right:
                    return person_box

        return None

    @cached_property
    def person_boxes(self) -> list[BoundingBox] | None:
        labels = self.label_name_to_value
        person = labels.get('person')

        if instances := person.instances:
            return [i.bounding_box for i in instances]

        return None


@dataclass
class Label:
    """
    Label dataclass

    """
    name: str
    confidence: float
    instances: List['Instance']
    parents: List['Parent']


@dataclass
class Instance:
    """
    Instance dataclass

    """
    bounding_box: 'BoundingBox'
    confidence: float


@dataclass
class Parent:
    """
    Parent dataclass

    """
    name: str


@dataclass
class CompareFacesResp(JSONWizard):
    """
    Response from the Rekognition CompareFaces API

    """
    source_image_face: 'SourceImageFace'
    face_matches: List['FaceMatch']
    unmatched_faces: List['UnmatchedFace']


@dataclass
class SourceImageFace:
    """
    SourceImageFace dataclass

    """
    bounding_box: 'BoundingBox'
    confidence: float


@dataclass
class FaceMatch:
    """
    FaceMatch dataclass

    """
    similarity: float
    face: 'Face'


@dataclass
class UnmatchedFace:
    """
    UnmatchedFace dataclass

    """
    bounding_box: 'BoundingBox'
    confidence: float
    landmarks: List['Landmark']
    pose: 'Pose'
    quality: 'Quality'


@dataclass
class DetectFacesResp(JSONWizard):
    """
    Response from the Rekognition DetectFaces API

    """
    face_details: List['FaceDetail']

    def get_face(self) -> Optional['FaceDetail']:
        """
        Return the primary face that is detected, if available.
        """

        try:
            return self.face_details[0]
        except IndexError:
            return None


@dataclass
class FaceDetail:
    """
    FaceDetail dataclass

    """
    bounding_box: 'BoundingBox'
    age_range: 'AgeRange'
    smile: 'Smile'
    eyeglasses: 'Eyeglasses'
    sunglasses: 'Sunglasses'
    gender: 'Gender'
    beard: 'Beard'
    mustache: 'Mustache'
    eyes_open: 'EyesOpen'
    mouth_open: 'MouthOpen'
    emotions: List['Emotion']
    landmarks: List['Landmark']
    pose: 'Pose'
    quality: 'Quality'
    confidence: float

    @cached_property
    def emotion_to_confidence(self) -> DictWithLowerStore[str, float]:
        """
        Return a case-insensitive mapping of emotion name to its confidence.
        """
        return DictWithLowerStore(
            {e.type: e.confidence for e in self.emotions})


@dataclass
class BoundingBox:
    """
    BoundingBox dataclass

    """
    width: float
    height: float
    left: float
    top: float


@dataclass
class AgeRange:
    """
    AgeRange dataclass

    """
    low: int
    high: int


@dataclass
class Smile:
    """
    Smile dataclass

    """
    value: bool
    confidence: float


@dataclass
class Eyeglasses:
    """
    Eyeglasses dataclass

    """
    value: bool
    confidence: float


@dataclass
class Sunglasses:
    """
    Sunglasses dataclass

    """
    value: bool
    confidence: float


@dataclass
class Gender:
    """
    Gender dataclass

    """
    value: str
    confidence: float


@dataclass
class Beard:
    """
    Beard dataclass

    """
    value: bool
    confidence: float


@dataclass
class Mustache:
    """
    Mustache dataclass

    """
    value: bool
    confidence: float


@dataclass
class EyesOpen:
    """
    EyesOpen dataclass

    """
    value: bool
    confidence: float


@dataclass
class MouthOpen:
    """
    MouthOpen dataclass

    """
    value: bool
    confidence: float


@dataclass
class Emotion:
    """
    Emotion dataclass

    """
    type: str
    confidence: float


@dataclass
class Landmark:
    """
    Landmark dataclass

    """
    type: str
    x: float
    y: float


@dataclass
class Pose:
    """
    Pose dataclass

    """
    roll: float
    yaw: float
    pitch: float


@dataclass
class Quality:
    """
    Quality dataclass

    """
    brightness: float
    sharpness: float
