# Expense Tracker

A desktop app for recording everyday expenses and reviewing monthly totals by category. Entries are saved in a local SQLite database and stay on this device. The app uses only Python's standard library, including Tkinter and SQLite.

## Run

From this folder, run:

```bash
python app.py
```

Enter the date, description, category, and amount, then select **Add expense**. Use the month controls to browse records. To remove an entry, select it and confirm deletion. Use one currency consistently; amounts are stored as entered and are not converted.

The database is saved at `~/.python-mini/expenses.sqlite3` (inside your home folder). It is not saved in this project folder or uploaded anywhere.

## Run the Tests

```bash
python -m unittest
```