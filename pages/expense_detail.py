import datetime
from decimal import Decimal
from typing import Annotated

from fastapi import APIRouter, Depends, Form, HTTPException, Request, status
from fastapi.responses import RedirectResponse

from dependencies import get_expense_service, get_messaging_service
from models.expense import CATEGORIES, Expense
from services.expense_service import ExpenseService
from services.messaging_service import MessagingService
from templating import templates

router = APIRouter()


def find_expense(expense_service: ExpenseService, expense_id: int) -> Expense:
    """Returns the expense with the given id; if there is no such expense, the answer is 404 Not Found."""
    expense = expense_service.get_expense(expense_id)
    if expense is None:
        raise HTTPException(status_code=404, detail="Expense not found")
    return expense


@router.get("/expensedetail/{expense_id}")
def show(
    request: Request,
    expense_id: int,
    expense_service: Annotated[ExpenseService, Depends(get_expense_service)],
):
    """The parameter expense_id gets its value from the path of the address: /expensedetail/3"""
    expense = find_expense(expense_service, expense_id)

    return templates.TemplateResponse(request, "expense_detail.html", {"expense": expense})


@router.post("/expensedetail/{expense_id}")
def save(
    expense_id: int,
    expense_service: Annotated[ExpenseService, Depends(get_expense_service)],
    messaging_service: Annotated[MessagingService, Depends(get_messaging_service)],
    date: Annotated[datetime.date, Form()],
    amount: Annotated[Decimal, Form()],
    description: Annotated[str, Form()] = "",
    category: Annotated[str, Form()] = "Other",
):
    expense = find_expense(expense_service, expense_id)
    description = description.strip()

    if description == "" or amount <= 0:
        messaging_service.add("Not saved: the description must not be empty, and the amount must be greater than zero.")
    else:
        expense.date = date
        expense.description = description
        expense.category = category if category in CATEGORIES else "Other"
        expense.amount = amount
        expense_service.update(expense)
        messaging_service.add(f"Saved: {expense.description}")

    # navigate back to the page of this expense
    return RedirectResponse(f"/expensedetail/{expense.id}", status_code=status.HTTP_303_SEE_OTHER)
