from __future__ import annotations

from boto3 import Session, client
from botocore.config import Config
from botocore.exceptions import ClientError

from .client_cache import ClientCache
from ...log import LOG


class S3Helper(ClientCache):
    """
    Helper class for interacting with the `boto3` S3 client.
    """

    SERVICE_NAME = 's3'

    def __init__(self, region_name='us-east-1', profile_name=None,
                 access_key: str | None = None, secret_key: str | None = None,
                 use_sig_v4=False, init_client=False,
                 max_pool_connections=None):

        self.access_key = access_key
        self.secret_key = secret_key
        self.use_sig_v4 = use_sig_v4

        super().__init__(region_name, profile_name, init_client,
                         max_pool_connections=max_pool_connections)

    def _create_client(self):
        client_kwargs = {}
        config_kwargs = {}

        if self.THREAD_SAFE or self.profile_name:
            client_func = Session(profile_name=self.profile_name).client
        else:
            client_func = client

        if self.access_key and self.secret_key:
            # Using access keys from an IAM user
            client_kwargs['aws_access_key_id'] = self.access_key
            client_kwargs['aws_secret_access_key'] = self.secret_key

        if self.max_pool_connections:
            config_kwargs['max_pool_connections'] = self.max_pool_connections

        if self.use_sig_v4:
            # Get the service client with signature v4 configured
            LOG.info('Creating S3 client with sigv4 configured')
            config_kwargs['signature_version'] = 's3v4'

        if config_kwargs:
            client_kwargs['config'] = Config(**config_kwargs)

        return client_func(self.SERVICE_NAME, self.region_name, **client_kwargs)

    def get_object_bytes(self, bucket, key) -> bytes:
        """
        Retrieve an object (raw bytes) from S3.
        """
        try:
            res = self.client.get_object(Bucket=bucket, Key=key)

        except ClientError as ce:
            error_data = ce.response['Error']
            LOG.error('Error retrieving object, error data: %s', str(error_data))
            raise

        return res['Body'].read()
