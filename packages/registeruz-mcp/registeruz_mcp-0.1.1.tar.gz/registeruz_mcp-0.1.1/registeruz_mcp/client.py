"""HTTP client for the RegisterUZ API."""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

import httpx

BASE_URL = "https://www.registeruz.sk/cruz-public"
API_BASE = f"{BASE_URL}/api"
DEFAULT_TIMEOUT = 30.0


@asynccontextmanager
async def get_client() -> AsyncGenerator[httpx.AsyncClient, None]:
    """Create an async HTTP client for API requests."""
    async with httpx.AsyncClient(
        base_url=API_BASE,
        timeout=DEFAULT_TIMEOUT,
        headers={"Accept": "application/json"},
    ) as client:
        yield client


def get_attachment_download_url(attachment_id: int) -> str:
    """Get the download URL for an attachment."""
    return f"{BASE_URL}/domain/financialreport/attachment/{attachment_id}"


def get_financial_report_pdf_download_url(report_id: int) -> str:
    """Get the PDF download URL for a financial report."""
    return f"{BASE_URL}/domain/financialreport/pdf/{report_id}"
