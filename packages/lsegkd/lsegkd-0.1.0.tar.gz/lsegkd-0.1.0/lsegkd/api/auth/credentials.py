import os


LSEG_KNOWLEDGE_DIRECT_API_BASE_URL: str = "https://api.rkd.refinitiv.com/"


class Credentials:
    """A class to manage credentials for accessing the LSEG Knowledge Direct API."""

    def __init__(
        self,
        *,
        username: str | None = None,
        app_id: str | None = None,
        password: str | None = None,
        base_url: str | None = None,
    ):
        """
        Initialize the Credentials object with provided or environment variable values.

        Args:
            username (str, optional): The username for authentication.
                Defaults to None. If None, it will be fetched from the
                environment variable 'LSEG_KNOWLEDGE_DIRECT_USERNAME'.
            app_id (str, optional): The application ID for authentication.
                Defaults to None. If None, it will be fetched from the
                environment variable 'LSEG_KNOWLEDGE_DIRECT_APP_ID'.
            password (str, optional): The password for authentication.
                Defaults to None. If None, it will be fetched from the
                environment variable 'LSEG_KNOWLEDGE_DIRECT_PASSWORD'.
            base_url (str, optional): The base URL for the API.
                Defaults to None. If None, it will use the default
                LSEG_KNOWLEDGE_DIRECT_API_BASE_URL.

        Raises:
            ValueError: If any of the required credentials are not provided.
        """
        self.username = username or os.getenv("LSEG_KNOWLEDGE_DIRECT_USERNAME")
        self.app_id = app_id or os.getenv("LSEG_KNOWLEDGE_DIRECT_APP_ID")
        self.password = password or os.getenv("LSEG_KNOWLEDGE_DIRECT_PASSWORD")
        self.base_url = base_url or LSEG_KNOWLEDGE_DIRECT_API_BASE_URL

        if not self.is_valid():
            raise ValueError(
                "Credentials are not fully set. Please provide username, app_id, and password."
            )

    def is_valid(self) -> bool:
        """
        Check if the credentials are valid (i.e., all required fields are set).

        Returns:
            bool: True if all required fields are set, False otherwise.
        """
        return all([self.username, self.app_id, self.password])
