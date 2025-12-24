from typing import List, Dict
from .base import AbstractAsyncBankSource, AbstractBankSource, SourceValue
from .utils import load_data, aload_data, parse_data


class BCCBankSource(AbstractBankSource):
    """Synchronous BCC Bank source for currency exchange rates."""

    def __init__(self, url: str = "https://www.bcc.cd/"):
        self.url = url
        self._cache: Dict[str, SourceValue] = {}
        self._cache_valid = False

    def get_value(self, cur: str) -> SourceValue:
        """Get exchange rate for a specific currency."""
        cur = cur.upper()

        if not self._cache_valid:
            self.sync(cache=True)

        if cur in self._cache:
            return self._cache[cur]

        raise ValueError(f"Currency {cur} not found in BCC rates")

    def get_values(
        self, curs: List[str] | None = None
    ) -> List[SourceValue]:
        """Get exchange rates for multiple currencies."""
        if not self._cache_valid:
            self.sync(cache=True)

        if curs is None:
            return list(self._cache.values())

        result = []
        for cur in curs:
            cur = cur.upper()
            if cur in self._cache:
                result.append(self._cache[cur])

        return result

    def sync(self, cache=True) -> List[SourceValue]:
        """Synchronize exchange rates from BCC website."""
        html_content = load_data(self.url)
        if html_content is None:
            raise ConnectionError(f"Failed to load data from {self.url}")

        rates = parse_data(html_content)

        if cache:
            self._cache = {rate.currency: rate for rate in rates}
            self._cache_valid = True

        return rates


class AsyncBCCBankSource(AbstractAsyncBankSource):
    """Asynchronous BCC Bank source for currency exchange rates."""

    def __init__(self, url: str = "https://www.bcc.cd/"):
        self.url = url
        self._cache: Dict[str, SourceValue] = {}
        self._cache_valid = False

    async def get_value(self, cur: str) -> SourceValue:
        """Get exchange rate for a specific currency."""
        cur = cur.upper()

        if not self._cache_valid:
            await self.sync(cache=True)

        if cur in self._cache:
            return self._cache[cur]

        raise ValueError(f"Currency {cur} not found in BCC rates")

    async def get_values(
        self, curs: List[str] | None = None
    ) -> List[SourceValue]:
        """Get exchange rates for multiple currencies."""
        if not self._cache_valid:
            await self.sync(cache=True)

        if curs is None:
            return list(self._cache.values())

        result = []
        for cur in curs:
            cur = cur.upper()
            if cur in self._cache:
                result.append(self._cache[cur])

        return result

    async def sync(self, cache=True) -> List[SourceValue]:
        """Synchronize exchange rates from BCC website."""
        html_content = await aload_data(self.url)
        if html_content is None:
            raise ConnectionError(f"Failed to load data from {self.url}")

        rates = parse_data(html_content)

        if cache:
            self._cache = {rate.currency: rate for rate in rates}
            self._cache_valid = True

        return rates
