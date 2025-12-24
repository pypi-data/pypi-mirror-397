from lsegkd.api.services.base.client import BaseServiceClient
from lsegkd.api.services.token_management.methods import (
    CreateServiceToken,
    CreateServiceTokenResponse,
)


class TokenManagementServiceClient(BaseServiceClient):
    """Client for the Token Management service of the LSEG Knowledge Direct API."""

    service_path: str = (
        "/api/TokenManagement/TokenManagement.svc/REST/Anonymous/TokenManagement_1/"
    )
    use_http: bool = False

    def create_service_token(
        self,
        *,
        timeout: int = 30,
    ) -> CreateServiceTokenResponse:
        """
        Create a service token using the Token Management service.

        Args:
            timeout (int, optional): The timeout for the request in seconds.
                Defaults to 30.
            return_raw_response (bool, optional): Whether to return the raw response.
                Defaults to False.

        Returns:
            CreateServiceTokenResponse: The response containing the service token and its expiration.
        """
        return CreateServiceToken(
            self.service_url_base,
            self.credentials,
        ).get(timeout=timeout)
