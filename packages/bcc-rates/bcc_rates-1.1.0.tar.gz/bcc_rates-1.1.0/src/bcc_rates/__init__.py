from .bcc import BCCBankSource, AsyncBCCBankSource
from .oxr import OXRBankSource, AsyncOXRBankSource
from .base import SourceValue, AbstractBankSource, AbstractAsyncBankSource

__all__ = [
    "BCCBankSource",
    "AsyncBCCBankSource",
    "OXRBankSource",
    "AsyncOXRBankSource",
    "SourceValue",
    "AbstractBankSource",
    "AbstractAsyncBankSource",
]

__version__ = "1.1.0"
__author__ = "Oxiliere <dev@oxiliere.com>"
__email__ = "dev@oxiliere.com"
__url__ = "https://github.com/oxiliere/bcc_rates"
__description__ = "Exchange rate fetching library for BCC and OXR APIs"
__license__ = "MIT"
