import datetime

import httpx

from lsegkd.api.auth import Credentials
from lsegkd.api.services.base.client import BaseServiceClient
from lsegkd.api.services.street_events.methods import (
    GetEventHeadlines,
    GetEventHeadlinesResponse,
    GetDocument,
    Status,
)


class StreetEventsServiceClient(BaseServiceClient):
    """
    Client for the Street Events service of the LSEG Knowledge Direct API.
    """

    service_path: str = "/api/StreetEvents/StreetEvents.svc/REST/StreetEvents_2/"
    use_http: bool = False

    def __init__(
        self, credentials: Credentials, token: str, *, async_mode: bool = False
    ):
        """
        Initialize the StreetEventsServiceClient with provided credentials.

        Args:
            credentials (Credentials): An instance of the Credentials class.
        """
        super().__init__(credentials=credentials)
        self.token = token
        self._async_client = httpx.AsyncClient() if async_mode else None

    def get_event_headlines(
        self,
        *,
        page_number: int = 1,
        records_per_page: int = 1000,
        from_date: datetime.datetime | None = None,
        to_date: datetime.datetime | None = None,
        countries: list[str] = ["US"],
        transcript_status: Status | None = "Final",
        utc_indicator_in_response: bool = False,
        timeout: int = 30,
    ) -> GetEventHeadlinesResponse:
        """
        Retrieve event headlines from the Street Events service.

        Args:
            page_number (int): The page number for pagination. Default is 1.
            records_per_page (int): The number of records per page. Default is 1000.
            from_date (datetime.datetime): The start date for the event headlines. Default is None.
            to_date (datetime.datetime): The end date for the event headlines. Default is None.
            countries (list[str]): List of country codes to filter the headlines. Default is ["US"].
            transcript_status (str): The transcript status filter. Default is "Final".
            utc_indicator_in_response (bool): Whether to include UTC indicator in the response. Default is False.
            timeout (int): Timeout for the request in seconds. Default is 30.

        Returns:
            GetEventHeadlinesResponse: The response from the GetEventHeadlines API.
        """
        return GetEventHeadlines(
            self.service_url_base, self.credentials, token=self.token
        ).get(
            page_number=page_number,
            records_per_page=records_per_page,
            from_date=from_date,
            to_date=to_date,
            countries=countries,
            transcript_status=transcript_status,
            utc_indicator_in_response=utc_indicator_in_response,
            timeout=timeout,
        )

    def get_document(
        self,
        transcript_id: str,
        *,
        timeout: int = 30,
    ) -> str:
        """
        Retrieve a document in XML format from the Street Events service.

        Args:
            transcript_id (str): The ID of the transcript.
            timeout (int): Timeout for the request in seconds. Default is 30.

        Returns:
            str: The content of the document in XML format.
        """
        return GetDocument(
            self.service_url_base,
            self.credentials,
            token=self.token,
        ).get(transcript_id=transcript_id, timeout=timeout)

    async def aget_document(
        self,
        transcript_id: str,
        *,
        timeout: int = 30,
    ) -> str:
        """
        Asynchronously retrieve a document in XML format from the Street Events service.

        Args:
            transcript_id (str): The ID of the transcript.
            timeout (int): Timeout for the request in seconds. Default is 30.
        Returns:
            str: The content of the document in XML format.
        """
        if self._async_client is None:
            raise ValueError("Async client is not initialized.")

        return await GetDocument(
            self.service_url_base,
            self.credentials,
            token=self.token,
            _async_client=self._async_client,
        ).aget(transcript_id=transcript_id, timeout=timeout)
