import datetime
from typing import Literal

import requests
from loguru import logger

from lsegkd.api.services.base import BaseMethod


class GetDocument(BaseMethod):
    """Method to get a document from the Street Events service."""

    path: str = "GetDocument_1"
    document_url_template: str = "https://api.rkd.refinitiv.com/api/streetevents/documents/{transcript_id}/Transcript/Xml.ashx"

    @staticmethod
    def _create_payload(
        transcript_id: str,
        document_type: str,
        document_format: str,
        document_last_modified_date: datetime.datetime | None,
        decode_document: Literal[True] = True,
        private_network_url: Literal[False] = False,
    ) -> dict:
        """
        Create the payload for the GetDocument API request.
        """
        return {
            "GetDocument_Request_1": {
                "DocumentId": transcript_id,
                "DocumentType": document_type,
                "DocumentFormat": document_format,
                "DocumentLastModifiedDate": document_last_modified_date,
                "DecodeDocument": decode_document,
                "PrivateNetworkURL": private_network_url,
            }
        }

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

    def get_document_url(
        self,
        transcript_id: str,
        *,
        document_type: Literal["Transcript"] = "Transcript",
        document_format: Literal["Xml"] = "Xml",
        document_last_modified_date: datetime.datetime | None = None,
        decode_document: Literal[True] = True,
        private_network_url: Literal[False] = False,
        timeout: int = 30,
    ) -> str:
        """
        Retrieve a document URL from the Street Events service.

        Args:
            transcript_id (str): The ID of the transcript.
            document_type (Literal["Transcript"]): The type of the document. Default is "Transcript".
            document_format (Literal["Xml"]): The format of the document. Default is "Xml".
            document_last_modified_date (datetime.datetime | None): The last modified date of the document. Default is None.
            decode_document (bool): Whether to decode the document. Default is True.
            private_network_url (bool): Whether to use a private network URL. Default is False.
            timeout (int): Timeout for the request in seconds. Default is 30.

        Returns:
            dict: The response from the GetDocument API.
        """
        payload = self._create_payload(
            transcript_id=transcript_id,
            document_type=document_type,
            document_format=document_format,
            document_last_modified_date=document_last_modified_date,
            decode_document=decode_document,
            private_network_url=private_network_url,
        )
        headers = self._create_headers()
        response = requests.post(
            self.url,
            json=payload,
            headers=headers,
            timeout=timeout,
        )

        response.raise_for_status()

        url = response.json().get("GetDocument_Response_1", {}).get("DocumentURLSecure")
        return url

    async def aget_document_url(
        self,
        transcript_id: str,
        *,
        document_type: Literal["Transcript"] = "Transcript",
        document_format: Literal["Xml"] = "Xml",
        document_last_modified_date: datetime.datetime | None = None,
        decode_document: Literal[True] = True,
        private_network_url: Literal[False] = False,
        timeout: int = 30,
    ) -> str:
        """
        Asynchronously retrieve a document URL from the Street Events service.

        Args:
            transcript_id (str): The ID of the transcript.
            document_type (Literal["Transcript"]): The type of the document. Default is "Transcript".
            document_format (Literal["Xml"]): The format of the document. Default is "Xml".
            document_last_modified_date (datetime.datetime | None): The last modified date of the document. Default is None.
            decode_document (bool): Whether to decode the document. Default is True.
            private_network_url (bool): Whether to use a private network URL. Default is False.
            timeout (int): Timeout for the request in seconds. Default is 30.

        Returns:
            dict: The response from the GetDocument API.
        """
        payload = self._create_payload(
            transcript_id=transcript_id,
            document_type=document_type,
            document_format=document_format,
            document_last_modified_date=document_last_modified_date,
            decode_document=decode_document,
            private_network_url=private_network_url,
        )

        headers = self._create_headers()

        if self._async_client is None:
            raise ValueError("Async client is not initialized.")

        response = await self._async_client.post(
            self.url,
            json=payload,
            headers=headers,
            timeout=timeout,
        )

        response.raise_for_status()
        return (
            response.json().get("GetDocument_Response_1", {}).get("DocumentURLSecure")
        )

    def _get_xml_from_url(
        self,
        url: str,
        *,
        timeout: int = 30,
    ) -> str:
        """
        Internal method to get (XML) the document content from a URL.


        Args:
            url (str): The URL of the document.
            timeout (int): Timeout for the request in seconds. Default is 30.

        Returns:
            str: The content of the document.
        """
        response = requests.get(
            url,
            timeout=timeout,
        )

        response.raise_for_status()

        return response.text

    async def _aget_xml_from_url(
        self,
        url: str,
        *,
        timeout: int = 30,
    ) -> str:
        if self._async_client is None:
            raise ValueError("Async client is not initialized.")

        response = await self._async_client.get(url, timeout=timeout)

        response.raise_for_status()
        return response.text

    def get(
        self,
        transcript_id: str,
        *,
        timeout: int = 30,
    ) -> str:
        """
        Retrieve a document from the Street Events service.

        Args:
            transcript_id (str): The ID of the transcript.
            timeout (int): Timeout for the request in seconds. Default is 30.

        Returns:
            str: The content of the document.
        """

        xml = None
        try:
            url = self.document_url_template.format(transcript_id=transcript_id)
            logger.info(f"Trying to retrieve document from standard URL: {url}")
            xml = self._get_xml_from_url(
                url,
                timeout=timeout,
            )
        except Exception:
            logger.info("Falling back to GetDocument API to retrieve document URL.")
            url = self.get_document_url(transcript_id)
            logger.info(f"Trying to retrieve document from fallback URL: {url}")
            xml = self._get_xml_from_url(
                url,
                timeout=timeout,
            )
        finally:
            if not xml:
                raise ValueError("Failed to retrieve document.")

        return xml

    async def aget(
        self,
        transcript_id: str,
        *,
        timeout: int = 30,
    ) -> str:
        xml = None

        try:
            url = self.document_url_template.format(transcript_id=transcript_id)
            logger.info(f"Trying standard URL: {url}")
            xml = await self._aget_xml_from_url(url, timeout=timeout)

        except Exception:
            logger.info("Fallback to GetDocument API")
            url = await self.aget_document_url(transcript_id)
            logger.info(f"Trying fallback URL: {url}")
            xml = await self._aget_xml_from_url(url, timeout=timeout)

        if not xml:
            raise ValueError("Failed to retrieve document.")

        return xml
