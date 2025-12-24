import datetime

import requests
from pydantic import BaseModel

from lsegkd.api.utils import parse_datetime
from lsegkd.api.services.base import BaseMethod


class CreateServiceTokenResponse(BaseModel):
    """Response model for the CreateServiceToken operation."""

    token: str
    expiration: datetime.datetime

    @staticmethod
    def from_response(response: dict) -> "CreateServiceTokenResponse":
        """
        Parse the response from the Token Management service to create a CreateServiceTokenResponse object.

        Args:
            response (dict): The response from the Token Management service.

        Returns:
            CreateServiceTokenResponse: The parsed response object.
        """
        token_response = response.get("CreateServiceToken_Response_1")

        if not token_response:
            raise ValueError(
                "Invalid response format: missing 'CreateServiceToken_Response_1'"
            )

        token = token_response.get("Token")
        if not token:
            raise ValueError("Invalid response format: missing 'Token'")

        expiration_str = token_response.get("Expiration")
        if not expiration_str:
            raise ValueError("Invalid response format: missing 'Expiration'")

        return CreateServiceTokenResponse(
            token=token, expiration=parse_datetime(expiration_str)
        )


class CreateServiceToken(BaseMethod):
    """Method to create a service token using the Token Management service."""

    path: str = "CreateServiceToken_1"

    def _create_payload(self) -> dict:
        """
        Create the payload for the CreateServiceToken API request.

        Returns:
            dict: The payload for the API request.
        """
        return {
            "CreateServiceToken_Request_1": {
                "ApplicationID": self.credentials.app_id,
                "Username": self.credentials.username,
                "Password": self.credentials.password,
            }
        }

    def get(
        self,
        *,
        timeout: int = 30,
    ) -> CreateServiceTokenResponse:
        """
        Create a service token using the Token Management service.

        Args:
            timeout (int, optional): Timeout for the request in seconds.
                Defaults to 30.
            return_raw_response (bool, optional): Whether to return the raw response.
                Defaults to False.

        Returns:
            CreateServiceTokenResponse: The response containing the service token and its expiration.
        """
        payload = self._create_payload()
        response = requests.post(
            self.url,
            json=payload,
            timeout=timeout,
        )

        response.raise_for_status()
        return CreateServiceTokenResponse.from_response(response.json())
