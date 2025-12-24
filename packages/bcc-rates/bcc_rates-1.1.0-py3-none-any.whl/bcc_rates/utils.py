import re
import requests
import aiohttp
from typing import List, Optional
from decimal import Decimal, InvalidOperation
from bs4 import BeautifulSoup
from .base import SourceValue


def parse_data(html_content: str) -> List[SourceValue]:
    """Parse HTML content to extract currency exchange rates.

    Args:
        html_content: HTML string containing currency data

    Returns:
        List of SourceValue objects with currency codes and rates in CDF
    """
    soup = BeautifulSoup(html_content, "html.parser")
    currency_data = []

    # Find all currency rows
    rows = soup.find_all("div", class_="changes_row")

    for row in rows:
        try:
            # Extract currency code
            currency_elem = row.find("div", class_="devise")
            if not currency_elem:
                continue
            currency_code = currency_elem.get_text(strip=True)

            # Extract value (rate in CDF)
            value_elem = row.find("div", class_="valeur")
            if not value_elem:
                continue

            # Get the text and remove the CDF span
            value_text = value_elem.get_text(strip=True)
            # Remove 'CDF' from the end if present
            value_text = re.sub(r"\s*CDF\s*$", "", value_text)
            # Remove spaces and convert commas to dots for decimal parsing
            value_text = value_text.replace(" ", "").replace(",", ".")

            # Convert to Decimal for precision
            rate = Decimal(value_text)

            currency_data.append(SourceValue(currency=currency_code, amount=rate))

        except (ValueError, AttributeError, InvalidOperation) as e:
            # Skip invalid entries
            continue

    return currency_data


def load_data(url: str, timeout: int = 30) -> Optional[str]:
    """Load HTML content from URL synchronously.

    Args:
        url: URL to fetch data from
        timeout: Request timeout in seconds

    Returns:
        HTML content as string, or None if request fails
    """
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        response = requests.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        print(f"Error loading data from {url}: {e}")
        return None


async def aload_data(url: str, timeout: int = 30) -> Optional[str]:
    """Load HTML content from URL asynchronously.

    Args:
        url: URL to fetch data from
        timeout: Request timeout in seconds

    Returns:
        HTML content as string, or None if request fails
    """
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

        timeout_config = aiohttp.ClientTimeout(total=timeout)
        async with aiohttp.ClientSession(timeout=timeout_config) as session:
            async with session.get(url, headers=headers) as response:
                response.raise_for_status()
                return await response.text()

    except aiohttp.ClientError as e:
        print(f"Error loading data from {url}: {e}")
        return None
