import datetime
from abc import ABC, abstractmethod
from decimal import Decimal

from models.expense import Expense


class ExpenseService(ABC):
    """
    What a page may ask for when it needs expenses.

    This class only says WHAT can be done (it is an abstract class, an "interface").
    HOW it is done is written in a class that inherits from it - see FileExpenseService.
    The pages know only about ExpenseService, so the place where the expenses are kept
    (a file now, a database in the project) can be changed without changing the pages.
    """

    @abstractmethod
    def get_expenses(self) -> list[Expense]:
        """Returns all the expenses, the newest first."""

    @abstractmethod
    def get_expense(self, expense_id: int) -> Expense | None:
        """Returns the expense with the given id, or None if there is no such expense."""

    @abstractmethod
    def add(self, date: datetime.date, description: str, category: str, amount: Decimal) -> Expense:
        """Adds a new expense and returns it."""

    @abstractmethod
    def update(self, expense: Expense) -> None:
        """Saves the changes made to an expense."""

    @abstractmethod
    def delete(self, expense_id: int) -> None:
        """Removes the expense with the given id."""

    def filter(self, category: str = "", month: str = "", text: str = "") -> list[Expense]:
        """
        Returns the expenses of the given category, in the given month ("2026-11"),
        whose description contains the given text. An empty value means "any".

        This method is not abstract: it is written once, here, using get_expenses(),
        so every class that inherits from ExpenseService gets it for free.
        """
        result = []
        for expense in self.get_expenses():
            if category != "" and expense.category != category:
                continue
            if month != "" and expense.month() != month:
                continue
            # lower() makes the comparison independent of upper and lower case letters
            if text != "" and text.lower() not in expense.description.lower():
                continue
            result.append(expense)
        return result

    def totals_by_category(self, expenses: list[Expense]) -> dict[str, Decimal]:
        """Adds up the amounts of the given expenses per category, the largest total first."""
        totals: dict[str, Decimal] = {}
        for expense in expenses:
            totals[expense.category] = totals.get(expense.category, Decimal("0")) + expense.amount
        # sorted() with key= sorts the pairs (category, total) by the total; reverse=True - from the largest
        return dict(sorted(totals.items(), key=lambda pair: pair[1], reverse=True))
