from datetime import date
from pathlib import Path
import tempfile
import unittest

from tracker import ExpenseBook, amount_to_cents


class ExpenseBookTests(unittest.TestCase):
    def setUp(self):
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.database_path = Path(self.temporary_directory.name) / "expenses.sqlite3"
        self.book = ExpenseBook(self.database_path)

    def tearDown(self):
        self.temporary_directory.cleanup()

    def test_monthly_records_totals_and_categories(self):
        self.book.add("2026-04-03", "Lunch", "Food", 1250)
        self.book.add("2026-04-11", "Bus pass", "Transport", 3200)
        self.book.add("2026-05-01", "Coffee", "Food", 450)

        april = self.book.for_month(2026, 4)

        self.assertEqual([expense.description for expense in april], ["Bus pass", "Lunch"])
        self.assertEqual(self.book.month_totals(2026, 4), (4450, 2))
        self.assertEqual(
            self.book.category_totals(2026, 4),
            [("Transport", 3200), ("Food", 1250)],
        )

    def test_records_persist_and_can_be_deleted(self):
        expense_id = self.book.add("2026-04-03", "Lunch", "Food", 1250)

        reopened_book = ExpenseBook(self.database_path)

        self.assertEqual(len(reopened_book.for_month(2026, 4)), 1)
        self.assertTrue(reopened_book.delete(expense_id))
        self.assertFalse(reopened_book.delete(expense_id))
        self.assertEqual(reopened_book.month_totals(2026, 4), (0, 0))

    def test_add_rejects_invalid_date_and_empty_description(self):
        with self.assertRaises(ValueError):
            self.book.add("2026-02-30", "Lunch", "Food", 1250)
        with self.assertRaises(ValueError):
            self.book.add(date.today().isoformat(), "  ", "Food", 1250)

    def test_amount_conversion_keeps_exact_cents(self):
        self.assertEqual(amount_to_cents("1,234.56".replace(",", "")), 123456)
        with self.assertRaises(ValueError):
            amount_to_cents("12.345")
        with self.assertRaises(ValueError):
            amount_to_cents("0")


if __name__ == "__main__":
    unittest.main()