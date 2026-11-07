# My Expenses - Homework 2

A personal expense tracker: a web application made with **FastAPI** and **Jinja2 templates**.
You enter what you spent money on, and the application shows the list, filters it, and adds up the totals
for each month and category.

It is built the same way as the course application *Vanity Fair* (module 04, folders `01-actors-new` ... `13-actors-service-search`):
the same folders, the same kind of services, dependency injection, components and messages.
If something here is unclear, look at the same file in `04-python-fastapi-actors/13-actors-service-search`.

## Starting the application

Once, in this folder (the terminal of VS Code):

```text
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

Every time:

```text
.venv\Scripts\activate
python main.py
```

Then open <http://localhost:8000>. Stop the server with `Ctrl+C` in the terminal.

## What the application can do

| Page | Address | What it does |
|---|---|---|
| Dashboard | `/dashboard` | the total of the month, the number of expenses, the largest one; a bar for every category; the five newest expenses; arrows for the previous and next month (`/dashboard?month=2026-10`) |
| Expenses | `/expenses` | the table of all the expenses with the total; a form for adding; a filter by category, month and text (`/expenses?category=Food&month=2026-10&text=pizza`); a button for deleting |
| Expense detail | `/expensedetail/3` | one expense, and a form for changing it |

The expenses are saved in `data/expenses.json` after every change, so they are still there after a restart.
On the first start this file is made as a copy of `sample-data/expenses.json`.
**To start again with the sample data, stop the server and delete the folder `data`.**

## The files

| File or folder | What it contains |
|---|---|
| `main.py` | creates the application, adds the pages to it, and shows the page *Invalid input* when a value in a form cannot be understood |
| `models/expense.py` | the class `Expense` (a `@dataclass`) and the list of categories `CATEGORIES` |
| `services/expense_service.py` | `ExpenseService` - an abstract class: WHAT can be done with the expenses. `filter()` and `totals_by_category()` are written here, once |
| `services/file_expense_service.py` | `FileExpenseService` - HOW it is done: reads and writes a JSON file |
| `services/messaging_service.py` | the messages at the bottom of every page, with listeners (the same as in the course) |
| `dependencies.py` | makes one object of each service, and the functions that hand them to the pages (dependency injection) |
| `templating.py` | the template engine; the filter `money` (`{{ e.amount \| money }}` shows `1,234.50 RSD`); `categories` available in every template |
| `pages/dashboard.py`, `pages/expenses.py`, `pages/expense_detail.py`, `pages/messages.py` | one module per page: the functions that answer the requests (`@router.get`, `@router.post`) |
| `templates/layout.html` | the frame of every page: Bootstrap, the menu, the messages |
| `templates/nav_menu.html` | the menu (Bootstrap *navbar*) |
| `templates/dashboard.html`, `expenses.html`, `expense_detail.html`, `invalid_input.html` | the pages |
| `templates/components/` | the components (Jinja2 macros): `ExpenseForm`, `CategoryTotals`, `AppMessages` |
| `static/css/app.css` | a few styles of our own (Bootstrap does the rest) |

## What happens when an expense is added - from the click to the new page

1. The form in the component `ExpenseForm` is sent with `method="post"` to `/expenses`.
2. FastAPI finds the function with `@router.post("/expenses")` - `add()` in `pages/expenses.py`.
3. The values of the form become the parameters of the function (`Form()`), converted to the right types:
   `date` to `datetime.date`, `amount` to `Decimal`. If that is not possible, `invalid_input()` in `main.py` answers.
4. `Depends(get_expense_service)` gives the function the expense service - the function does not create it.
5. The function checks the values (the description must not be empty, the amount must be greater than zero),
   asks the service to add the expense, and adds a message.
6. It answers with a redirect (`303 See Other`) to `/expenses`, so the browser asks for the list again with GET.
   (Without it, refreshing the page would send the form again and add the expense twice.)
7. `show()` in `pages/expenses.py` gets the expenses from the service and gives them to the template `expenses.html`,
   which makes the HTML with a `{% for %}` loop.

## Things to be able to explain

- **GET or POST?** The filter uses GET: it only reads, and its values are in the address, so a filtered list can be
  bookmarked. Adding, changing and deleting use POST, because they change the data.
- **Why `Decimal` and not `float`?** Money must be exact. With `float`, `0.1 + 0.2` is `0.30000000000000004`.
- **Why an abstract class `ExpenseService`?** The pages only know about `ExpenseService`. In the project, the expenses
  will come from a RESTful service and a database: only a new class (for example `RestExpenseService`) and one line in
  `dependencies.py` will change - the pages stay the same.
- **Why is the form checked on the server too, when the browser already checks `required` and `min`?**
  A request can be sent without the browser (for example with `curl`), so the server must never trust the data.
- **What is a component?** A Jinja2 macro: a piece of HTML with parameters. `ExpenseForm` is used on two pages -
  empty for adding, filled for changing.
- **What does `{% extends "layout.html" %}` do?** The page takes the whole frame from `layout.html` and fills only
  `{% block content %}`.

## Ideas, if you want to add something of your own

- a monthly budget per category, and a red bar when it is exceeded;
- sorting the table by clicking on the column headers (`/expenses?sort=amount`);
- income as well as expenses, and the balance of the month;
- a page with the totals of the whole year, month by month.

## Publishing on GitHub

Create a new repository on GitHub (without a README), then, in this folder:

```text
git init
git add .
git commit -m "Homework 2: My Expenses"
git branch -M main
git remote add origin https://github.com/YOUR-NAME/expense-tracker.git
git push -u origin main
```

The file `.gitignore` keeps `.venv`, `__pycache__` and `data` out of the repository.
