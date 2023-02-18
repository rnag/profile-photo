from __future__ import annotations

import json
from dataclasses import dataclass

from .client_cache import ClientCache
from .rekognition_models import DetectLabelsResp, DetectFacesResp
from ...log import LOG


@dataclass
class Rekognition(ClientCache):
    SERVICE_NAME = 'rekognition'

    def detect_labels(self, bucket: str, key: str, im_bytes: bytes | None = None,
                      debug=False, confidence=55):
        """
        Call the DetectLabels API on an image, or use the DynamoDB cache if
        needed.

        https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/rekognition.html#Rekognition.Client.detect_labels
        """
        resp = self.client.detect_labels(
            Image=self._im_param(bucket, key, im_bytes),
            MinConfidence=confidence,
        )

        if debug:
            LOG.info('Detect Labels Response:\n  %s', json.dumps(resp))

        return DetectLabelsResp.from_dict(resp)

    def detect_faces(self, bucket: str, key: str, im_bytes: bytes | None = None,
                     debug=False, all_attrs=True):
        """
        Call the DetectFaces API on an image, or use the DynamoDB cache if
        needed.

        https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/rekognition.html#Rekognition.Client.detect_faces
        """

        kwargs = {
            'Attributes': ['ALL'] if all_attrs else ['DEFAULT'],
            'Image': self._im_param(bucket, key, im_bytes)
        }

        resp = self.client.detect_faces(**kwargs)

        if debug:
            LOG.info('Detect Faces Response:\n  %s', json.dumps(resp))

        return DetectFacesResp.from_dict(resp)

    def recognize_celebrities(self, bucket: str, key: str, im_bytes: bytes | None = None):
        """
        Call the RecognizeCelebrities API on an image, or use the DynamoDB
        cache if needed.

        https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/rekognition.html#Rekognition.Client.recognize_celebrities
        """
        return self.client.recognize_celebrities(
            Image=self._im_param(bucket, key, im_bytes))

    @staticmethod
    def _im_param(s3_bucket: str = None,
                  s3_key: str = None,
                  im_bytes: bytes | None = None):
        """
        Build the input for the `Image` parameter to use in a Rekognition API
        call.
        """
        if s3_bucket:
            bucket_info = {
                'Bucket': s3_bucket,
                'Name': s3_key
            }
            return {'S3Object': bucket_info}
        else:
            return {'Bytes': im_bytes}
