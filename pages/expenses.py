import datetime
from decimal import Decimal
from typing import Annotated

from fastapi import APIRouter, Depends, Form, Request, status
from fastapi.responses import RedirectResponse

from dependencies import get_expense_service, get_messaging_service
from models.expense import CATEGORIES
from services.expense_service import ExpenseService
from services.messaging_service import MessagingService
from templating import templates

router = APIRouter()


@router.get("/expenses")
def show(
    request: Request,
    expense_service: Annotated[ExpenseService, Depends(get_expense_service)],
    category: str = "",
    month: str = "",
    text: str = "",
):
    """
    The filter form uses the method GET, so its values travel in the address:
    /expenses?category=Food&month=2026-11&text=pizza
    """
    found = expense_service.filter(category, month, text)
    total = sum((e.amount for e in found), Decimal("0"))

    return templates.TemplateResponse(
        request,
        "expenses.html",
        {
            "expenses": found,
            "total": total,
            "category": category,
            "month": month,
            "text": text,
            "today": datetime.date.today(),
        },
    )


@router.post("/expenses")
def add(
    expense_service: Annotated[ExpenseService, Depends(get_expense_service)],
    messaging_service: Annotated[MessagingService, Depends(get_messaging_service)],
    date: Annotated[datetime.date, Form()],
    amount: Annotated[Decimal, Form()],
    description: Annotated[str, Form()] = "",
    category: Annotated[str, Form()] = "Other",
):
    """The values of the form are converted by FastAPI: the date into datetime.date, the amount into Decimal."""
    description = description.strip()

    # the browser checks the form too, but the server must not trust it - a request can come from anywhere
    if description == "":
        messaging_service.add("The expense was not added: the description is empty.")
    elif amount <= 0:
        messaging_service.add("The expense was not added: the amount must be greater than zero.")
    else:
        if category not in CATEGORIES:
            category = "Other"
        expense = expense_service.add(date, description, category, amount)
        messaging_service.add(f"Added: {expense.description} ({expense.amount} RSD)")

    return RedirectResponse("/expenses", status_code=status.HTTP_303_SEE_OTHER)


@router.post("/expenses/{expense_id}/delete")
def delete(
    expense_id: int,
    expense_service: Annotated[ExpenseService, Depends(get_expense_service)],
    messaging_service: Annotated[MessagingService, Depends(get_messaging_service)],
):
    """
    An HTML form can send only GET and POST requests,
    so the request for deleting is a POST to an address that ends with /delete.
    """
    expense = expense_service.get_expense(expense_id)
    if expense is not None:
        expense_service.delete(expense_id)
        messaging_service.add(f"Deleted: {expense.description}")

    return RedirectResponse("/expenses", status_code=status.HTTP_303_SEE_OTHER)
