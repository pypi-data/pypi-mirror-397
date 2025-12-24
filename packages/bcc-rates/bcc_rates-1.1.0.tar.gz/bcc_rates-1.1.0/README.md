# 🏦 BCC Rates

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**BCC Rates** is a Python library and command-line tool for fetching real-time currency exchange rates from multiple sources including the **Banque Centrale du Congo (BCC)** and **Open Exchange Rates (OXR)**. It provides both synchronous and asynchronous APIs for seamless integration into your applications.

## 🌟 Features

- 📊 **Multiple data sources**: BCC official website and Open Exchange Rates API
- 🔄 **Synchronous and asynchronous** API support
- 💱 **Currency conversion** with precise calculations
- 🔀 **Backend comparison** - Compare rates from different sources
- 🖥️ **Command-line interface** for quick conversions
- 🎯 **Interactive mode** for multiple conversions
- ⚡ **Async mode** for better performance
- 🔧 **Type hints** for better development experience

## 🚀 Installation

### From PyPI (recommended)
```bash
pip install bcc-rates
```

### From GitHub
```bash
pip install git+https://github.com/oxiliere/bcc_rates.git
```

### From source (development)
```bash
git clone https://github.com/oxiliere/bcc_rates.git
cd bcc_rates
pip install -e .
```

### Using uv (recommended for development)
```bash
git clone https://github.com/oxiliere/bcc_rates.git
cd bcc_rates
uv sync
```

## 📖 Quick Start

### Command Line Usage

After installation, use the `bcc_exchange` command:

```bash
# Show all available exchange rates (BCC by default)
bcc_exchange --list

# Convert currencies
bcc_exchange 100 USD EUR

# Use OXR backend
bcc_exchange --backend oxr 100 USD EUR

# Compare rates from both sources
bcc_exchange --compare

# Interactive mode
bcc_exchange --interactive

# Async mode for better performance
bcc_exchange --async-mode 100 USD EUR

# Quiet mode (result only)
bcc_exchange --quiet 1000 EUR CDF
```

### Python API

#### Synchronous Usage

```python
from bcc_rates import BCCBankSource, OXRBankSource
from dinero import Dinero, currencies

# Initialize the BCC source
bcc = BCCBankSource()

# Get all exchange rates
rates = bcc.sync()
print(f"Found {len(rates)} exchange rates")

# Get specific currency rate
usd_rate = bcc.get_value("USD")
print(f"1 USD = {usd_rate.amount} CDF")

# Currency conversion
amount = Dinero(100, currencies.USD)
converted = bcc.to(amount, "EUR")
print(f"100 USD = {converted.amount} EUR")

# Using OXR backend
import os
os.environ['OXR_API_KEY'] = 'your_api_key_here'

oxr = OXRBankSource()
rates = oxr.sync()
oxr.set_cdf_as_base()  # Convert to CDF base
usd_rate = oxr.get_value("USD")
print(f"1 USD = {usd_rate.amount} CDF (from OXR)")
```

#### Asynchronous Usage

```python
import asyncio
from bcc_rates import AsyncBCCBankSource, AsyncOXRBankSource
from dinero import Dinero, currencies

async def main():
    # Initialize async BCC source
    bcc = AsyncBCCBankSource()
    
    # Get all exchange rates
    rates = await bcc.sync()
    print(f"Found {len(rates)} exchange rates")
    
    # Get specific currency rate
    eur_rate = await bcc.get_value("EUR")
    print(f"1 EUR = {eur_rate.amount} CDF")
    
    # Currency conversion
    amount = Dinero(50, currencies.GBP)
    converted = await bcc.to(amount, "USD")
    print(f"50 GBP = {converted.amount} USD")
    
    # Parallel fetching from multiple sources
    oxr = AsyncOXRBankSource()
    bcc_rates, oxr_rates = await asyncio.gather(
        bcc.sync(),
        oxr.sync()
    )
    print(f"BCC: {len(bcc_rates)} rates, OXR: {len(oxr_rates)} rates")

# Run async function
asyncio.run(main())
```

## 🛠️ Command Line Interface

The `bcc_exchange` command provides a powerful CLI for currency operations:

### Basic Commands

```bash
# Show help
bcc_exchange --help

# List all available currencies and rates
bcc_exchange --list

# Convert 100 USD to EUR
bcc_exchange 100 USD EUR

# Convert 1000 EUR to CDF (Congolese Franc)
bcc_exchange 1000 EUR CDF

# Use async mode for better performance
bcc_exchange --async-mode 50 GBP USD
```

### Backend Selection

```bash
# Use BCC backend (default)
bcc_exchange --backend bcc --list
bcc_exchange -b bcc 100 USD EUR

# Use OXR backend (requires API key)
export OXR_API_KEY="your_api_key_here"
bcc_exchange --backend oxr --list
bcc_exchange -b oxr 100 USD CDF

# Compare rates from both sources
bcc_exchange --compare
bcc_exchange -c

# Compare with async mode (faster)
bcc_exchange --compare --async-mode
bcc_exchange -c -a
```

### Interactive Mode

```bash
# Interactive mode with BCC
bcc_exchange --interactive

# Interactive mode with OXR
bcc_exchange --backend oxr --interactive
```

This starts an interactive session where you can perform multiple conversions:

```
🔄 Interactive Currency Converter (BCC)
Enter 'quit' to exit
------------------------------
Available currencies: AOA, AUD, BIF, CAD, CDF, CHF, CNY, EUR, GBP, JPY, RWF, TZS, UGX, USD, XAF, XDR, ZAR, ZMW

Enter amount (or 'quit'): 100
From currency: USD
To currency: EUR
✅ 100.00 USD = 86.15 EUR

Enter amount (or 'quit'): quit
```

### Quiet Mode

For scripting and automation:

```bash
# Returns only the conversion result
bcc_exchange --quiet 100 USD EUR
# Output: 86.1487
```

## 📚 API Reference

### Classes

#### `BCCBankSource` (Synchronous)

```python
class BCCBankSource:
    def __init__(self, url: str = "https://www.bcc.cd/"):
        """Initialize BCC source with optional custom URL."""
    
    def sync(self, cache: bool = True) -> List[SourceValue]:
        """Fetch all exchange rates from BCC."""
    
    def get_value(self, currency: str) -> SourceValue:
        """Get exchange rate for specific currency."""
    
    def get_values(self, currencies: List[str] = None) -> List[SourceValue]:
        """Get exchange rates for multiple currencies."""
    
    def to(self, base: Dinero, target: str | Currency) -> Dinero:
        """Convert currency amount to target currency."""
```

#### `OXRBankSource` (Synchronous)

```python
class OXRBankSource:
    def __init__(self, api_key: str = None):
        """Initialize OXR source with API key (or from OXR_API_KEY env var)."""
    
    def sync(self, cache: bool = True) -> List[SourceValue]:
        """Fetch all exchange rates from OXR API."""
    
    def set_cdf_as_base(self):
        """Convert rates to use CDF as base currency (same format as BCC)."""
    
    def get_value(self, currency: str) -> SourceValue:
        """Get exchange rate for specific currency."""
    
    def get_values(self, currencies: List[str] = None) -> List[SourceValue]:
        """Get exchange rates for multiple currencies."""
    
    def to(self, base: Dinero, target: str | Currency) -> Dinero:
        """Convert currency amount to target currency."""
```

#### `AsyncBCCBankSource` (Asynchronous)

```python
class AsyncBCCBankSource:
    def __init__(self, url: str = "https://www.bcc.cd/"):
        """Initialize async BCC source with optional custom URL."""
    
    async def sync(self, cache: bool = True) -> List[SourceValue]:
        """Fetch all exchange rates from BCC."""
    
    async def get_value(self, currency: str) -> SourceValue:
        """Get exchange rate for specific currency."""
    
    async def get_values(self, currencies: List[str] = None) -> List[SourceValue]:
        """Get exchange rates for multiple currencies."""
    
    async def to(self, base: Dinero, target: str | Currency) -> Dinero:
        """Convert currency amount to target currency."""
```

#### `AsyncOXRBankSource` (Asynchronous)

```python
class AsyncOXRBankSource:
    def __init__(self, api_key: str = None):
        """Initialize async OXR source with API key (or from OXR_API_KEY env var)."""
    
    async def sync(self, cache: bool = True) -> List[SourceValue]:
        """Fetch all exchange rates from OXR API."""
    
    def set_cdf_as_base(self):
        """Convert rates to use CDF as base currency (same format as BCC)."""
    
    async def get_value(self, currency: str) -> SourceValue:
        """Get exchange rate for specific currency."""
    
    async def get_values(self, currencies: List[str] = None) -> List[SourceValue]:
        """Get exchange rates for multiple currencies."""
    
    async def to(self, base: Dinero, target: str | Currency) -> Dinero:
        """Convert currency amount to target currency."""
```

#### `SourceValue`

```python
@dataclass
class SourceValue:
    currency: str  # Currency code (e.g., "USD", "EUR")
    amount: Decimal  # Exchange rate in CDF
```

### Supported Currencies

#### BCC Backend
Supports all currencies available on the BCC website (~17 currencies):
- **USD** - US Dollar
- **EUR** - Euro
- **GBP** - British Pound
- **CAD** - Canadian Dollar
- **CHF** - Swiss Franc
- **JPY** - Japanese Yen
- **CNY** - Chinese Yuan
- **AUD** - Australian Dollar
- **ZAR** - South African Rand
- **CDF** - Congolese Franc (base currency)
- And more...

#### OXR Backend
Supports 170+ currencies from Open Exchange Rates API, including all major world currencies.

**Note:** OXR requires an API key. Get one free at [openexchangerates.org](https://openexchangerates.org/)

## 🧪 Development

### Setting up Development Environment

```bash
# Clone the repository
git clone https://github.com/oxiliere/bcc_rates.git
cd bcc_rates

# Install with uv (recommended)
uv sync

# Or with pip
pip install -e ".[dev]"
```

### Running Tests

```bash
# Run all tests
uv run python -m pytest

# Run with coverage
uv run python -m pytest --cov=bcc_rates

# Run specific test file
uv run python src/tests.py
```

### Running CLI in Development

```bash
# Using uv (recommended)
uv run python -m bcc_rates --help
uv run python -m bcc_rates 100 USD EUR

# Direct execution
uv run python src/bcc_rates/cli.py --help
```

### Code Quality

```bash
# Format code
uv run black src/

# Type checking
uv run mypy src/

# Linting
uv run flake8 src/
```

## 📋 Examples

### Basic Currency Conversion

```python
from bcc_rates import BCCBankSource
from dinero import currencies, Dinero

bcc = BCCBankSource()

# Convert 100 USD to EUR
usd_amount = Dinero(100, currencies.USD)
eur_amount = bcc.to(usd_amount, "EUR")
print(f"100 USD = {eur_amount.amount:.2f} EUR")

# Convert 1000 EUR to CDF
eur_amount = Dinero(1000, currencies.EUR)
cdf_amount = bcc.to(eur_amount, "CDF")
print(f"1000 EUR = {cdf_amount.amount:,.2f} CDF")
```

### Batch Processing

```python
from bcc_rates import BCCBankSource

bcc = BCCBankSource()

# Get rates for specific currencies
currencies_of_interest = ["USD", "EUR", "GBP", "CAD"]
rates = bcc.get_values(currencies_of_interest)

for rate in rates:
    print(f"1 {rate.currency} = {rate.amount:,.4f} CDF")
```

### Async Batch Processing

```python
import asyncio
from bcc_rates import AsyncBCCBankSource

async def get_multiple_rates():
    bcc = AsyncBCCBankSource()
    
    # Fetch all rates
    rates = await bcc.sync()
    
    # Process rates
    major_currencies = ["USD", "EUR", "GBP", "JPY"]
    for currency in major_currencies:
        try:
            rate = await bcc.get_value(currency)
            print(f"1 {currency} = {rate.amount:,.4f} CDF")
        except ValueError:
            print(f"{currency} not available")

asyncio.run(get_multiple_rates())
```

### Comparing Multiple Sources

```python
import asyncio
from bcc_rates import AsyncBCCBankSource, AsyncOXRBankSource

async def compare_sources():
    bcc = AsyncBCCBankSource()
    oxr = AsyncOXRBankSource()
    
    # Fetch from both sources in parallel
    bcc_rates, oxr_rates = await asyncio.gather(
        bcc.sync(),
        oxr.sync()
    )
    
    # Convert OXR to CDF base
    oxr.set_cdf_as_base()
    
    # Compare USD rates
    bcc_usd = await bcc.get_value("USD")
    oxr_usd = await oxr.get_value("USD")
    
    print(f"BCC: 1 USD = {bcc_usd.amount:,.4f} CDF")
    print(f"OXR: 1 USD = {oxr_usd.amount:,.4f} CDF")
    print(f"Difference: {abs(bcc_usd.amount - oxr_usd.amount):,.4f} CDF")

asyncio.run(compare_sources())
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

### Development Guidelines

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Write tests** for your changes
4. **Ensure** all tests pass
5. **Commit** your changes (`git commit -m 'Add amazing feature'`)
6. **Push** to the branch (`git push origin feature/amazing-feature`)
7. **Open** a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Banque Centrale du Congo (BCC)** for providing the exchange rate data
- **Open Exchange Rates** for their comprehensive currency API
- **Dinero** library for currency handling
- **BeautifulSoup** for HTML parsing
- **aiohttp** for async HTTP requests
- **requests** for synchronous HTTP requests

## 📞 Support

If you encounter any issues or have questions:

1. Check the [Issues](https://github.com/oxiliere/bcc_rates/issues) page
2. Create a new issue if your problem isn't already reported
3. Provide detailed information about your environment and the issue

## 🔗 Links

- **PyPI Package**: [https://pypi.org/project/bcc-rates/](https://pypi.org/project/bcc-rates/)
- **Source Code**: [https://github.com/oxiliere/bcc_rates](https://github.com/oxiliere/bcc_rates)
- **BCC Official Website**: [https://www.bcc.cd/](https://www.bcc.cd/)

---

Made with ❤️ for the Congolese developer community
