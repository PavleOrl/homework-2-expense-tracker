"""
Homework 2: My Expenses - a personal expense tracker, made with FastAPI and Jinja2 templates.

Pages:
    /dashboard              the totals of one month, per category, and the latest expenses
    /expenses               all the expenses: filtering, adding, deleting
    /expensedetail/{id}     one expense: its details and a form for changing it

Start it with      python main.py
and then open      http://localhost:8000
"""

import uvicorn
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

from pages import dashboard, expense_detail, expenses, messages
from templating import BASE_DIR, templates

app = FastAPI(title="My Expenses")
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")

app.include_router(dashboard.router)
app.include_router(expenses.router)
app.include_router(expense_detail.router)
app.include_router(messages.router)


@app.get("/")
def index():
    """The application starts with the dashboard."""
    return RedirectResponse("/dashboard")


@app.exception_handler(RequestValidationError)
def invalid_input(request: Request, exc: RequestValidationError):
    """
    FastAPI calls this function when a value cannot be converted
    (for example, a text where a number or a date is expected).
    Instead of an error in the JSON format, the user gets a page that explains it.
    """
    return templates.TemplateResponse(request, "invalid_input.html", {"errors": exc.errors()}, status_code=422)


if __name__ == "__main__":
    uvicorn.run("main:app", port=8000, reload=True)
