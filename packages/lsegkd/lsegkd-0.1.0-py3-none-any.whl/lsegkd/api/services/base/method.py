from abc import ABC
from urllib.parse import urljoin

import httpx
from lsegkd.api.auth import Credentials


class BaseMethod(ABC):
    """Abstract base class for LSEG Knowledge Direct API methods."""

    path: str  # should be defined in subclasses

    def __init__(
        self,
        service_url_base: str,
        credentials: Credentials,
        *,
        token: str | None = None,
        _async_client: httpx.AsyncClient | None = None,
    ):
        """
        Initialize the BaseClient with provided credentials.

        Args:
            service_url_base (str): The base URL for the service.
            credentials (Credentials): An instance of the Credentials class.
            token (str, optional): The service token for authentication.
                Defaults to None.
            async_mode (bool, optional): Whether to operate in asynchronous mode.
                Defaults to False.
        """
        self.service_url_base = service_url_base
        self.credentials = credentials
        self.token = token
        self._async_client = _async_client

    @property
    def url(self) -> str:
        """
        Construct the full URL for the method endpoint.

        Returns:
            str: The full URL for the method endpoint.
        """
        return urljoin(self.service_url_base, self.path)

    def set_token(self, token: str) -> None:
        """
        Set the service token for authentication.

        Args:
            token (str): The service token.
        """
        self.token = token
