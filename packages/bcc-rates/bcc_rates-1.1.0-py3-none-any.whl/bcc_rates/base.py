from typing import List
from decimal import Decimal
from dataclasses import dataclass
from abc import ABC, abstractmethod
from dinero.types import Currency
from dinero import currencies, Dinero
from .exceptions import InvalidCurrency


@dataclass(slots=True)
class SourceValue:
    currency: str
    amount: int | float | str | Decimal


class CurrencyMixin:
    """Mixin class providing currency validation functionality."""

    def get_currency(self, currency: str) -> Currency:
        currency = currency.upper()

        if hasattr(currencies, currency):
            return getattr(currencies, currency)

        raise InvalidCurrency(f"Invalid currency: {currency}")


class AbstractBankSource(ABC, CurrencyMixin):

    @abstractmethod
    def get_value(self, cur: str) -> SourceValue:
        pass

    @abstractmethod
    def get_values(
        self, curs: List[str] | None = None, cache=False
    ) -> List[SourceValue]:
        pass

    @abstractmethod
    def sync(self, cache=False) -> List[SourceValue]:
        pass

    def to(self, base: Dinero, to_cur: str | Currency) -> Dinero:
        currency: Currency = (
            self.get_currency(to_cur) if isinstance(to_cur, str) else to_cur
        )
        src = base.code
        dst = currency.get("code")

        if src == dst:
            return base

        if base.amount == 0:
            return Dinero(0, currency)

        src_value = self.get_value(src)
        dst_value = self.get_value(dst)

        src_amount = src_value.amount * base.amount
        dst_amount = src_amount / dst_value.amount if dst_value.amount > 0 else 0

        return Dinero(dst_amount, currency)


class AbstractAsyncBankSource(ABC, CurrencyMixin):

    @abstractmethod
    async def get_value(self, cur: str) -> SourceValue:
        pass

    @abstractmethod
    async def get_values(
        self, curs: List[str] | None = None, cache=False
    ) -> List[SourceValue]:
        pass

    @abstractmethod
    async def sync(self, cache=False) -> List[SourceValue]:
        pass

    async def to(self, base: Dinero, to_cur: str | Currency) -> Dinero:
        currency: Currency = (
            self.get_currency(to_cur) if isinstance(to_cur, str) else to_cur
        )
        src = base.code
        dst = currency.get("code")

        if src == dst:
            return base

        if base.amount == 0:
            return Dinero(0, currency)

        src_value = await self.get_value(src)
        dst_value = await self.get_value(dst)

        src_amount = src_value.amount * base.amount
        dst_amount = src_amount / dst_value.amount if dst_value.amount > 0 else 0

        return Dinero(dst_amount, currency)
