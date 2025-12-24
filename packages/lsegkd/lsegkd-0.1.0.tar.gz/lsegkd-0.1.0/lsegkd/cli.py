import asyncio
import datetime
import json
from pathlib import Path

import click
import dotenv
from loguru import logger

from lsegkd.api.auth import Credentials
from lsegkd.api.services.token_management import TokenManagementServiceClient
from lsegkd.api.services.street_events import StreetEventsServiceClient
from lsegkd.xml import EventTranscriptParser


def load_env(dotenv_path: str):
    """
    Load environment variables from a .env file.

    Args:
        dotenv_path (str): Path to the .env file.
    """
    if Path(dotenv_path).exists():
        dotenv.load_dotenv(dotenv_path)
        logger.info(f"Loaded environment variables from {dotenv_path}")
    else:
        logger.warning(
            f".env file not found at {dotenv_path}, proceeding without loading environment variables."
        )


async def load_document(
    record_per_page: int,
    from_date: datetime.datetime,
    to_date: datetime.datetime,
    countries: list[str],
    output_dir: str,
):
    """
    Load event documents and save them to the specified output directory.

    Args:
        record_per_page (int): Number of records to fetch per page.
        from_date (datetime.datetime): Start date for fetching events.
        to_date (datetime.datetime): End date for fetching events.
        countries (list[str]): List of country codes to filter events.
        output_dir (str): Path to the output directory.
    """
    if not Path(output_dir).exists():
        (Path(output_dir) / "xml").mkdir(parents=True, exist_ok=True)
        (Path(output_dir) / "headlines").mkdir(parents=True, exist_ok=True)
        (Path(output_dir) / "transcripts").mkdir(parents=True, exist_ok=True)
        logger.info(
            f"Created output directory at {output_dir}/xml and {output_dir}/headlines and {output_dir}/transcripts"
        )

    credentials = Credentials()
    logger.success("Credentials loaded successfully.")

    token_management_client = TokenManagementServiceClient(credentials=credentials)
    service_token = token_management_client.create_service_token()
    logger.success(
        f"Service token created successfully: {service_token.model_dump_json()}"
    )

    street_events_client = StreetEventsServiceClient(
        credentials=credentials,
        token=service_token.token,
        async_mode=True,
    )

    events = street_events_client.get_event_headlines(
        records_per_page=record_per_page,
        from_date=from_date,
        to_date=to_date,
        countries=countries,
        transcript_status="Final",
    )

    logger.info(events.extract_pagination_result())

    for headline in events.extract_event_headlines():
        if headline.Transcript is None:
            logger.info(
                f"No transcript available for this headline. {headline.EventType}"
            )
            continue

        logger.info(
            f"Fetching transcript for TranscriptId: {headline.Transcript.TranscriptId}, "
            f"EventId: {headline.EventId}, Status: {headline.Transcript.Status}"
        )
        try:
            xml = await street_events_client.aget_document(
                transcript_id=headline.Transcript.TranscriptId
            )
        except Exception as e:
            logger.error(
                f"Error fetching document for TranscriptId {headline.Transcript.TranscriptId} ({headline.Transcript.Status}): {e}"
            )
            continue

        output_path = Path(output_dir) / "xml" / f"{headline.EventId}.xml"
        with open(output_path, "w") as f:
            f.write(xml)
        logger.info(f"Transcript saved to {output_path}")

        headline_path = Path(output_dir) / "headlines" / f"{headline.EventId}.json"
        with open(headline_path, "w", encoding="utf-8") as f:
            json.dump(
                headline.model_dump(mode="json"),
                f,
                indent=4,
                ensure_ascii=False,
            )
        logger.info(f"Headline saved to {headline_path}")

        parser = EventTranscriptParser.from_string(xml)
        event = parser.parse()

        transcript_path = Path(output_dir) / "transcripts" / f"{headline.EventId}.json"
        with open(transcript_path, "w", encoding="utf-8") as f:
            json.dump(
                event.model_dump(mode="json"),
                f,
                indent=4,
                ensure_ascii=False,
            )
        logger.info(f"Parsed transcript saved to {transcript_path}")


@click.group()
@click.option(
    "-d", "--dotenv_path", default=".env", help="Path to the .env configuration file."
)
def cli(dotenv_path: str):
    """
    LSEG Knowledge Direct CLI.

    Args:
        dotenv_path (str): Path to the .env configuration file.
    """
    load_env(dotenv_path)


@cli.command("load-document")
@click.option(
    "--record_per_page",
    default=1000,
    help="Number of records to fetch per page. Default is 1000.",
)
@click.option(
    "--from_date", required=True, help="Start date for fetching events (YYYY-MM-DD)."
)
@click.option(
    "--to_date", required=True, help="End date for fetching events (YYYY-MM-DD)."
)
@click.option(
    "--countries",
    multiple=True,
    default=["US"],
    help="List of country codes to filter events. Default is US.",
)
@click.option("--output_dir", default="./output", help="Path to the output directory.")
def cli_load_document(
    record_per_page: int,
    from_date: str,
    to_date: str,
    countries: list[str],
    output_dir: str,
):
    """
    Load event documents and save them to the specified output directory.

    Args:
        record_per_page (int): Number of records to fetch per page.
        from_date (str): Start date for fetching events (YYYY-MM-DD).
        to_date (str): End date for fetching events (YYYY-MM-DD).
        countries (list[str]): List of country codes to filter events.
        output_dir (str): Path to the output directory.
    """
    from_date_dt = datetime.datetime.strptime(from_date, "%Y-%m-%d")
    to_date_dt = datetime.datetime.strptime(to_date, "%Y-%m-%d")

    asyncio.run(
        load_document(
            record_per_page=record_per_page,
            from_date=from_date_dt,
            to_date=to_date_dt,
            countries=countries,
            output_dir=output_dir,
        )
    )
