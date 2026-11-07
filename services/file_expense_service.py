import datetime
import json
import shutil
from decimal import Decimal
from pathlib import Path

from models.expense import Expense
from services.expense_service import ExpenseService
from services.messaging_service import MessagingService


class FileExpenseService(ExpenseService):
    """
    Keeps the expenses in a file in the JSON format.

    The expenses are read from the file once, kept in memory, and the file is written
    again after every change - so the expenses are still there after a restart.
    If the file does not exist yet, it is made as a copy of the sample data.
    """

    def __init__(self, file: Path, sample_file: Path, messaging_service: MessagingService):
        self._file = file
        self._messaging_service = messaging_service
        if not self._file.exists():
            self._file.parent.mkdir(exist_ok=True)
            shutil.copy(sample_file, self._file)
            self._messaging_service.add("ExpenseService: a new data file was made from the sample data")
        self._expenses: list[Expense] = self._read()

    def _read(self) -> list[Expense]:
        expenses = []
        for item in json.loads(self._file.read_text(encoding="utf-8")):
            expense = Expense(
                id=item["id"],
                date=datetime.date.fromisoformat(item["date"]),
                description=item["description"],
                category=item["category"],
                amount=Decimal(item["amount"]),
            )
            expenses.append(expense)
        return expenses

    def _save(self) -> None:
        items = []
        for expense in self._expenses:
            items.append(
                {
                    "id": expense.id,
                    "date": expense.date.isoformat(),
                    "description": expense.description,
                    "category": expense.category,
                    # JSON has no Decimal: the amount is written as text, so that it stays exact
                    "amount": str(expense.amount),
                }
            )
        self._file.write_text(json.dumps(items, indent=2, ensure_ascii=False), encoding="utf-8")

    def get_expenses(self) -> list[Expense]:
        # the newest first; for the same date, the one added later first
        return sorted(self._expenses, key=lambda e: (e.date, e.id), reverse=True)

    def get_expense(self, expense_id: int) -> Expense | None:
        for expense in self._expenses:
            if expense.id == expense_id:
                return expense
        return None

    def add(self, date: datetime.date, description: str, category: str, amount: Decimal) -> Expense:
        # the new expense gets the id that is by one greater than the greatest id in the list
        new_id = max((expense.id for expense in self._expenses), default=0) + 1
        expense = Expense(id=new_id, date=date, description=description, category=category, amount=amount)
        self._expenses.append(expense)
        self._save()
        return expense

    def update(self, expense: Expense) -> None:
        # the object from the list was changed directly by the page, so it only has to be saved
        self._save()

    def delete(self, expense_id: int) -> None:
        expense = self.get_expense(expense_id)
        if expense is not None:
            self._expenses.remove(expense)
            self._save()
