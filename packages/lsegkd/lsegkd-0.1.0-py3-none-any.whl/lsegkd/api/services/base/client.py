from abc import ABC
from urllib.parse import urljoin

from lsegkd.api.auth import Credentials


class BaseServiceClient(ABC):
    """Abstract base class for LSEG Knowledge Direct API clients."""

    service_path: str  # should be defined in subclasses
    use_http: bool = False  # Default to HTTPS

    def __init__(self, credentials: Credentials):
        """
        Initialize the BaseClient with provided credentials.

        Args:
            credentials (Credentials): An instance of the Credentials class.
        """
        self.credentials = credentials

    @property
    def service_url_base(self) -> str:
        """
        Construct the full URL for the service endpoint.

        Returns:
            str: The full URL for the service endpoint.
        """
        url = urljoin(self.credentials.base_url, self.service_path)
        if self.use_http:
            url = url.replace("https://", "http://")
        return url
