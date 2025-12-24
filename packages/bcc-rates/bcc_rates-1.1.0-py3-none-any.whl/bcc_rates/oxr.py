import os
from typing import List, Dict
import json
from .base import AbstractAsyncBankSource, AbstractBankSource, SourceValue
from .utils import load_data, aload_data, parse_data




OXR_API_KEY = os.getenv("OXR_API_KEY")
OXR_BASE_URL = "https://openexchangerates.org/api/latest.json"


class OXRBankSource(AbstractBankSource):
    def __init__(self, api_key: str = OXR_API_KEY):
        self.api_key = api_key
        self.base_url = OXR_BASE_URL
        self._cache: Dict[str, SourceValue] = {}
        self._cache_valid = False

        if not self.api_key:
            raise ValueError("OXR API key is required, please set OXR_API_KEY environment variable")
    
    def sync(self, cache=True) -> List[SourceValue]:
        """Synchronize exchange rates from OXR API."""
        url = f"{self.base_url}?app_id={self.api_key}&base=USD"
        rates = load_data(url)
        
        if rates is None:
            raise ConnectionError(f"Failed to load data from {url}")
        data = json.loads(rates)
        
        rates = data.get("rates", {})

        if cache:
            self._cache = {currency: SourceValue(currency=currency, amount=rate) for currency, rate in rates.items()}
            self._cache_valid = True

        return list(self._cache.values())

    def set_cdf_as_base(self):
        """Set CDF as the base currency in the cache.
        
        Converts rates from USD base (1 USD = X CDF) to CDF base (1 Currency = X CDF).
        After this, rates represent: 1 unit of currency = X CDF (same format as BCC).
        """
        
        if "CDF" in self._cache:
            cdf_rate = self._cache["CDF"].amount  # CDF per USD
            # Convert all rates to show CDF per unit of currency
            for currency in list(self._cache.keys()):
                if currency != "CDF":
                    usd_rate = self._cache[currency].amount  # This currency per USD
                    # To get CDF per this currency: (CDF/USD) / (Currency/USD) = CDF/Currency
                    cdf_per_currency = cdf_rate / usd_rate
                    self._cache[currency] = SourceValue(
                        currency=currency, 
                        amount=cdf_per_currency
                    )
            # Set CDF rate to 1 (1 CDF = 1 CDF)
            self._cache["CDF"] = SourceValue(currency="CDF", amount=1.0)

    def get_value(self, cur: str) -> SourceValue:
        """Get exchange rate for a specific currency."""
        cur = cur.upper()

        if not self._cache_valid:
            self.sync(cache=True)

        if cur in self._cache:
            return self._cache[cur]

        raise ValueError(f"Currency {cur} not found in OXR rates")

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

class AsyncOXRBankSource(AbstractAsyncBankSource):
    def __init__(self, api_key: str = OXR_API_KEY):
        self.api_key = api_key
        self.base_url = OXR_BASE_URL
        self._cache: Dict[str, SourceValue] = {}
        self._cache_valid = False

        if not self.api_key:
            raise ValueError("OXR API key is required, please set OXR_API_KEY environment variable")
    
    async def sync(self, cache=True) -> List[SourceValue]:
        """Synchronize exchange rates from OXR API."""
        
        url = f"{self.base_url}?app_id={self.api_key}&base=USD"
        rates = await aload_data(url)
        
        if rates is None:
            raise ConnectionError(f"Failed to load data from {url}")
        data = json.loads(rates)
        
        rates = data.get("rates", {})

        if cache:
            self._cache = {currency: SourceValue(currency=currency, amount=rate) for currency, rate in rates.items()}
            self._cache_valid = True

        return list(self._cache.values())

    def set_cdf_as_base(self):
        """Set CDF as the base currency in the cache.
        
        Converts rates from USD base (1 USD = X CDF) to CDF base (1 Currency = X CDF).
        After this, rates represent: 1 unit of currency = X CDF (same format as BCC).
        """
        
        if "CDF" in self._cache:
            cdf_rate = self._cache["CDF"].amount  # CDF per USD
            # Convert all rates to show CDF per unit of currency
            for currency in list(self._cache.keys()):
                if currency != "CDF":
                    usd_rate = self._cache[currency].amount  # This currency per USD
                    # To get CDF per this currency: (CDF/USD) / (Currency/USD) = CDF/Currency
                    cdf_per_currency = cdf_rate / usd_rate
                    self._cache[currency] = SourceValue(
                        currency=currency, 
                        amount=cdf_per_currency
                    )
            # Set CDF rate to 1 (1 CDF = 1 CDF)
            self._cache["CDF"] = SourceValue(currency="CDF", amount=1.0)

    async def get_value(self, cur: str) -> SourceValue:
        """Get exchange rate for a specific currency."""
        cur = cur.upper()

        if not self._cache_valid:
            await self.sync(cache=True)

        if cur in self._cache:
            return self._cache[cur]

        raise ValueError(f"Currency {cur} not found in OXR rates")

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

if __name__ == "__main__":
    import asyncio
    
    # Example usage - Sync
    print("=== Synchronous Example ===")
    oxr = OXRBankSource()
    oxr.sync(cache=True)
    oxr.set_cdf_as_base()
    print("USD:", oxr.get_value("USD"))
    print("EUR:", oxr.get_value("EUR"))
    print("CDF:", oxr.get_value("CDF"))
    print("Multiple:", oxr.get_values(["USD", "EUR", "CDF"]))
    print("All rates:", len(oxr.get_values()))
    
    # Example usage - Async
    async def async_example():
        print("\n=== Asynchronous Example ===")
        oxr_async = AsyncOXRBankSource()
        await oxr_async.sync(cache=True)
        oxr_async.set_cdf_as_base()
        print("USD:", await oxr_async.get_value("USD"))
        print("EUR:", await oxr_async.get_value("EUR"))
        print("CDF:", await oxr_async.get_value("CDF"))
        print("Multiple:", await oxr_async.get_values(["USD", "EUR", "CDF"]))
        print("All rates:", len(await oxr_async.get_values()))
    
    asyncio.run(async_example())
