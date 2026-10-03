# Expense Tracker

A desktop app for recording everyday expenses and reviewing monthly totals by category. Entries are saved in a local SQLite database and stay on this device. The app uses only Python's standard library, including Tkinter and SQLite.

## Run

From the repository root on Windows, run:

```bash
.venv\Scripts\python.exe projects\expense-tracker\app.py
```

If the virtual environment is already active, run:

```bash
python projects/expense-tracker/app.py
```

Or, from this project folder, run:

```bash
python app.py
```

Enter the date, description, category, and amount, then select **Add expense**. Use the month controls to browse records. To remove an entry, select it and confirm deletion. Use one currency consistently; amounts are stored as entered and are not converted.

The database is saved at `~/.python-mini/expenses.sqlite3` (inside your home folder). It is not saved in this project folder or uploaded anywhere.

## Run the Tests

```bash
python -m unittest
```

## GitHub Workflow

Run these commands from the repository root. To create a branch from the latest `main` and switch to it:

```bash
git switch main
git pull --ff-only origin main
git switch -c feature/expense-tracker
```

If the branch already exists, switch to it instead:

```bash
git switch feature/expense-tracker
```

Stage and review the project files, then commit with a short, descriptive message:

```bash
git add projects/expense-tracker
git diff --cached --check
git diff --cached --stat
git commit -m "feat: add desktop expense tracker"
```

Push the branch to GitHub:

```bash
git push -u origin feature/expense-tracker
```

Open a pull request to merge the branch into `main`, or merge locally after pushing:

```bash
git switch main
git pull --ff-only origin main
git merge --no-ff feature/expense-tracker
git push origin main
git branch -d feature/expense-tracker
```