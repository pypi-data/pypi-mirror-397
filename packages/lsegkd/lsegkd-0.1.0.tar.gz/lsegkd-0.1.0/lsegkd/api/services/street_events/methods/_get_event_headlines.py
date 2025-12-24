import datetime
from typing import Generator, Optional, Literal

import requests
from pydantic import BaseModel

from lsegkd.api.services.base import BaseMethod


Status = Literal["Preliminary", "Final", "Expected", "InProgress"]


class DurationModel(BaseModel):
    """Model representing the duration of an event."""

    StartDateTime: datetime.datetime
    StartQualifier: str
    EndDateTime: datetime.datetime
    EndQualifier: str
    IsEstimate: bool


class BriefModel(BaseModel):
    """Model representing a brief summary of an event."""

    BriefId: str
    Locale: str
    Status: Status


class TranscriptModel(BaseModel):
    """Model representing a transcript of an event."""

    TranscriptId: str
    Locale: str
    Status: Status
    DeliveryType: str


class SymbolModel(BaseModel):
    """Model representing a organization symbol."""

    Type: str
    Value: str


class SymbolsModel(BaseModel):
    """Model representing a collection of organization symbols."""

    Symbol: list[SymbolModel]


class OrganizationModel(BaseModel):
    """Model representing an organization."""

    Name: str
    Symbols: Optional[SymbolsModel] = None


class LiveDialInModel(BaseModel):
    """Model representing live dial-in information for an event."""

    Duration: DurationModel
    PhoneNumber: str
    Password: Optional[str]
    Status: str


class WebcastModel(BaseModel):
    """Model representing webcast information for an event."""

    Duration: DurationModel
    Provider: str
    Type: str
    Url: Optional[str]
    WebcastId: str


class EventHeadlineModel(BaseModel):
    """Model representing an event headline."""

    EventId: int
    EventType: str
    Name: str
    CountryCode: str
    LastUpdate: datetime.datetime

    Duration: DurationModel
    Brief: Optional[BriefModel] = None
    Organization: OrganizationModel

    LiveDialIn: Optional[LiveDialInModel] = None
    LiveWebcast: Optional[WebcastModel] = None
    ReplayWebcast: Optional[WebcastModel] = None

    Transcript: Optional[TranscriptModel] = None
    RsvpRequired: bool


class PagenationModel(BaseModel):
    """Model representing pagination details."""

    PageNumber: int
    RecordsOnPage: int
    RecordsPerPage: int
    TotalRecords: int


class GetEventHeadlinesResponse:
    """Response model for GetEventHeadlines API."""

    _root_key: str = "GetEventHeadlines_Response_1"

    def __init__(self, response: dict):
        self.response = response.get(self._root_key, {})

        if not self.response:
            raise ValueError("Invalid response format")

    def extract_event_headlines(self) -> Generator[EventHeadlineModel, None, None]:
        """
        Extract event headlines from the response data.

        Yields:
            Generator[EventHeadlineModel, None, None]: A generator of EventHeadlineModel objects.
        """
        if not self.response.get("EventHeadlines"):
            raise ValueError("No event headlines found in the response")

        for headline in self.response["EventHeadlines"].get("Headline", []):
            try:
                yield EventHeadlineModel.model_validate(headline)
            except Exception as e:
                raise ValueError(f"Error parsing headline: {headline}\n\n{e}")

    def extract_pagination_result(self) -> PagenationModel:
        """
        Extract pagination result from the response.

        Returns:
            PagenationModel: The pagination result extracted from the response.
        """
        if result := self.response.get("PaginationResult"):
            return PagenationModel.model_validate(result)
        raise ValueError("PaginationResult not found in response")


class GetEventHeadlines(BaseMethod):
    """Method to get event headlines using the Street Events service."""

    path: str = "GetEventHeadlines_1"

    @staticmethod
    def _create_payload(
        *,
        page_number: int = 1,
        records_per_page: int = 1000,
        from_date: datetime.datetime | None = None,
        to_date: datetime.datetime | None = None,
        countries: list[str] = ["US"],
        transcript_status: Status | None = "Final",
        utc_indicator_in_response: bool = False,
    ) -> dict:
        """
        Create the payload for the GetEventHeadlines API request.

        Args:
            page_number (int): The page number for pagination. Default is 1.
            records_per_page (int): The number of records per page. Default is 1000.
            from_date (datetime.datetime): The start date for the event headlines. Default is None.
            to_date (datetime.datetime): The end date for the event headlines. Default is None.
            countries (list[str]): List of country codes to filter the headlines. Default is ["US"].
            transcript_status (Literal["Preliminary", "Final", "Expected", "InProgress"] | None):
                The transcript status filter. Default is "Final".
            utc_indicator_in_response (bool): Whether to include UTC indicator in the response. Default is False.
        """
        parameters = {
            "UTCIndicatorInResponse": utc_indicator_in_response,
            "DateTimeRange": {
                "From": from_date.isoformat() if from_date else None,
                "To": to_date.isoformat() if to_date else None,
            },
            "Pagination": {
                "PageNumber": page_number,
                "RecordsPerPage": records_per_page,
            },
        }

        if countries:
            parameters["ContextCodes"] = (
                {
                    "Type": "Geography",
                    "Scheme": "",
                    "Values": {"Value": countries},
                },
            )

        if transcript_status is not None:
            parameters["ContentFilters"] = {
                "TranscriptFilter": [{"status": transcript_status}],
            }

        return {"GetEventHeadlines_Request_1": parameters}

    def _create_headers(self) -> dict:
        """
        Create the headers for the GetEventHeadlines API request.

        Returns:
            dict: The headers for the API request.
        """
        if self.token is None:
            raise ValueError("Authentication token is not set.")

        return {
            "Content-Type": "application/json; charset=utf-8",
            "X-Trkd-Auth-ApplicationID": self.credentials.app_id,
            "X-Trkd-Auth-Token": self.token,
        }

    def get(
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
        Get event headlines using the Street Events service.

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
        payload = self._create_payload(
            page_number=page_number,
            records_per_page=records_per_page,
            from_date=from_date,
            to_date=to_date,
            countries=countries,
            transcript_status=transcript_status,
            utc_indicator_in_response=utc_indicator_in_response,
        )
        headers = self._create_headers()
        response = requests.post(
            self.url,
            json=payload,
            headers=headers,
            timeout=timeout,
        )

        response.raise_for_status()

        return GetEventHeadlinesResponse(response.json())
