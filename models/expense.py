import datetime
from dataclasses import dataclass
from decimal import Decimal

# the categories that an expense can belong to (the same list is offered in every form)
CATEGORIES = ["Food", "Transport", "Housing", "Bills", "Health", "Education", "Fun", "Clothes", "Other"]


@dataclass
class Expense:
    """
    The model: the data that the application keeps about one expense.

    @dataclass writes the method __init__ for us, from the list of attributes below.
    The amount is a Decimal, not a float: money must be exact (0.1 + 0.2 is not exactly 0.3 with floats).
    """

    id: int
    date: datetime.date
    description: str
    category: str
    amount: Decimal

    def month(self) -> str:
        """The month of the expense as text, for example "2026-11" (the format of <input type="month">)."""
        return self.date.strftime("%Y-%m")
