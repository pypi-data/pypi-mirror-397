class BCCError(Exception):
    pass


class InvalidCurrency(BCCError):
    pass


class BankValueNotFound(BCCError):
    pass
