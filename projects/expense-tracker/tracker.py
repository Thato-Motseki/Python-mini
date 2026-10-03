from contextlib import closing
from dataclasses import dataclass
from datetime import date
from decimal import Decimal, InvalidOperation
from pathlib import Path
import sqlite3


DEFAULT_DATABASE = Path.home() / ".python-mini" / "expenses.sqlite3"


@dataclass(frozen=True)
class Expense:
    id: int
    spent_on: str
    description: str
    category: str
    amount_cents: int


def amount_to_cents(value: str) -> int:
    try:
        amount = Decimal(value.strip())
    except InvalidOperation as error:
        raise ValueError("Enter a valid amount, such as 12.50.") from error

    if not amount.is_finite() or amount <= 0:
        raise ValueError("Amount must be greater than zero.")

    cents = amount * 100
    if cents != cents.to_integral_value():
        raise ValueError("Use no more than two decimal places.")

    return int(cents)


class ExpenseBook:
    def __init__(self, database_path: Path = DEFAULT_DATABASE):
        self.database_path = Path(database_path)
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.database_path)
        connection.row_factory = sqlite3.Row
        return connection

    def _initialize(self) -> None:
        with closing(self._connect()) as connection, connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS expenses (
                    id INTEGER PRIMARY KEY,
                    spent_on TEXT NOT NULL,
                    description TEXT NOT NULL,
                    category TEXT NOT NULL,
                    amount_cents INTEGER NOT NULL CHECK (amount_cents > 0)
                )
                """
            )

    def add(
        self, spent_on: str, description: str, category: str, amount_cents: int
    ) -> int:
        try:
            date.fromisoformat(spent_on)
        except ValueError as error:
            raise ValueError("Enter a valid date in YYYY-MM-DD format.") from error

        description = description.strip()
        category = category.strip()
        if not description:
            raise ValueError("Add a short description for this expense.")
        if not category:
            raise ValueError("Choose a category.")
        if amount_cents <= 0:
            raise ValueError("Amount must be greater than zero.")

        with closing(self._connect()) as connection, connection:
            cursor = connection.execute(
                """INSERT INTO expenses (spent_on, description, category, amount_cents)
                   VALUES (?, ?, ?, ?)""",
                (spent_on, description, category, amount_cents),
            )
            return int(cursor.lastrowid)

    def for_month(self, year: int, month: int) -> list[Expense]:
        first_day = date(year, month, 1)
        if month == 12:
            following_month = date(year + 1, 1, 1)
        else:
            following_month = date(year, month + 1, 1)

        with closing(self._connect()) as connection, connection:
            rows = connection.execute(
                """SELECT id, spent_on, description, category, amount_cents
                   FROM expenses
                   WHERE spent_on >= ? AND spent_on < ?
                   ORDER BY spent_on DESC, id DESC""",
                (first_day.isoformat(), following_month.isoformat()),
            ).fetchall()

        return [Expense(**dict(row)) for row in rows]

    def month_totals(self, year: int, month: int) -> tuple[int, int]:
        first_day = date(year, month, 1)
        if month == 12:
            following_month = date(year + 1, 1, 1)
        else:
            following_month = date(year, month + 1, 1)

        with closing(self._connect()) as connection, connection:
            row = connection.execute(
                """SELECT COALESCE(SUM(amount_cents), 0) AS total, COUNT(*) AS count
                   FROM expenses
                   WHERE spent_on >= ? AND spent_on < ?""",
                (first_day.isoformat(), following_month.isoformat()),
            ).fetchone()

        return int(row["total"]), int(row["count"])

    def category_totals(self, year: int, month: int) -> list[tuple[str, int]]:
        first_day = date(year, month, 1)
        if month == 12:
            following_month = date(year + 1, 1, 1)
        else:
            following_month = date(year, month + 1, 1)

        with closing(self._connect()) as connection, connection:
            rows = connection.execute(
                """SELECT category, SUM(amount_cents) AS total
                   FROM expenses
                   WHERE spent_on >= ? AND spent_on < ?
                   GROUP BY category
                   ORDER BY total DESC, category ASC""",
                (first_day.isoformat(), following_month.isoformat()),
            ).fetchall()

        return [(str(row["category"]), int(row["total"])) for row in rows]

    def delete(self, expense_id: int) -> bool:
        with closing(self._connect()) as connection, connection:
            cursor = connection.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
            return cursor.rowcount > 0