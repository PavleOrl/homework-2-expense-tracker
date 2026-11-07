"""
The services of the application, and the functions that hand them over.

A function that needs a service does not create it. It only declares it as a parameter:

    def show(expense_service: Annotated[ExpenseService, Depends(get_expense_service)]):

Before FastAPI calls show(), it calls get_expense_service() and passes the result on.
This is called dependency injection. To keep the expenses somewhere else (for example
in a database), only this file has to be changed.
"""

from pathlib import Path

from services.expense_service import ExpenseService
from services.file_expense_service import FileExpenseService
from services.messaging_service import MessagingService

BASE_DIR = Path(__file__).parent


def write_message_to_console(messages: list[str]) -> None:
    """A listener: it is called by the messaging service whenever the messages change."""
    if messages:
        print("Message:", messages[-1])  # the last message of the list


# one object of each service for the whole application
_messaging_service = MessagingService()
_messaging_service.on_messages_changed.append(write_message_to_console)

_expense_service = FileExpenseService(
    BASE_DIR / "data" / "expenses.json",
    BASE_DIR / "sample-data" / "expenses.json",
    _messaging_service,
)


def get_messaging_service() -> MessagingService:
    return _messaging_service


def get_expense_service() -> ExpenseService:
    return _expense_service
