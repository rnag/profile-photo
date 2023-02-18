from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, InitVar
from typing import ClassVar

from boto3 import Session, client
from botocore.client import BaseClient
from botocore.config import Config
from botocore.exceptions import UnknownServiceError


@dataclass
class ClientCache:

    # boto3 service name
    SERVICE_NAME: ClassVar[str] = None

    # sub-classes can specify that client objects should be thread-safe
    THREAD_SAFE: ClassVar[bool] = False

    _clients: ClassVar[defaultdict] = defaultdict(dict)

    # The specified region that is bound to a client. Default to 'us-east-1'.
    region_name: str = 'us-east-1'

    # Optional AWS profile name.
    profile_name: str | None = None

    # When enabled, automatically initializes the client for the region; this
    # is useful when service requests will be made in multiple threads and it
    # is desirable to reuse the same client between threads.
    init_client: InitVar[bool] = False

    # Maximum pool connections for multi-thread usage
    # Ref: https://stackoverflow.com/a/68760777/10237506
    max_pool_connections: int | None = None

    def __post_init__(self, init_client: bool):
        self.region_name = self.region_name.lower()

        if init_client:
            _ = self.client

    @property
    def client(self):
        return self._get_client(self.region_name)

    @client.setter
    def client(self, value):
        raise Exception('Member read-only')

    def _get_client(self, region_name):
        """
        Internal method to return a low-level SecretManager client for a given region name
        """
        if region_name not in self._clients[self.SERVICE_NAME]:
            self._clients[self.SERVICE_NAME][region_name] = self._create_client()

        return self._clients[self.SERVICE_NAME][region_name]

    def _create_client(self) -> BaseClient:
        if not self.SERVICE_NAME:
            raise ValueError(
                'Sub-classes must provide a value for "SERVICE_NAME"')

        try:
            if self.THREAD_SAFE or self.profile_name:
                client_func = Session(profile_name=self.profile_name).client
            else:
                client_func = client

            client_kwargs = {}
            if self.max_pool_connections:
                client_kwargs['config'] = Config(
                    max_pool_connections=self.max_pool_connections)

            return client_func(self.SERVICE_NAME, self.region_name,
                               **client_kwargs)

        except UnknownServiceError:
            raise NotImplementedError(
                'Sub-classes must override this method')
