from datetime import date
from pathlib import Path
import tkinter as tk
from tkinter import messagebox, ttk

from tracker import DEFAULT_DATABASE, ExpenseBook, amount_to_cents


BACKGROUND = "#F1F5F2"
SURFACE = "#FFFFFF"
INK = "#1B302B"
MUTED = "#71817A"
LINE = "#DCE6E0"
GREEN = "#176B53"
GREEN_HOVER = "#105640"
MINT = "#E6F2EB"
GOLD = "#E9B74E"
CORAL = "#B95445"
CATEGORY_COLORS = ["#176B53", "#77A98D", "#E9B74E", "#D58167", "#7799A0", "#89966B"]
CATEGORIES = [
    "Food",
    "Transport",
    "Home",
    "Bills",
    "Health",
    "Shopping",
    "Education",
    "Other",
]


def format_amount(amount_cents: int) -> str:
    return f"{amount_cents / 100:,.2f}"


class ExpenseTrackerApp:
    def __init__(self, root: tk.Tk, book: ExpenseBook | None = None):
        self.root = root
        self.book = book or ExpenseBook(DEFAULT_DATABASE)
        self.visible_month = date.today().replace(day=1)
        self.expenses = []

        self.root.title("Morrow | Expense Tracker")
        self.root.geometry("1100x790")
        self.root.minsize(900, 700)
        self.root.configure(background=BACKGROUND)

        self.date_var = tk.StringVar(value=date.today().isoformat())
        self.description_var = tk.StringVar()
        self.category_var = tk.StringVar(value=CATEGORIES[0])
        self.amount_var = tk.StringVar()
        self.month_var = tk.StringVar()
        self.total_var = tk.StringVar(value="0.00")
        self.count_var = tk.StringVar(value="0")
        self.top_category_var = tk.StringVar(value="None yet")
        self.status_var = tk.StringVar(value="Your entries are saved on this device.")

        self._configure_styles()
        self._build_interface()
        self.refresh_month()

    def _configure_styles(self) -> None:
        style = ttk.Style(self.root)
        style.theme_use("clam")
        style.configure("App.TFrame", background=BACKGROUND)
        style.configure("Surface.TFrame", background=SURFACE)
        style.configure(
            "Field.TEntry",
            fieldbackground=SURFACE,
            foreground=INK,
            insertcolor=GREEN,
            padding=(10, 9),
            bordercolor=LINE,
            lightcolor=LINE,
            darkcolor=LINE,
            relief="flat",
        )
        style.configure(
            "Field.TCombobox",
            fieldbackground=SURFACE,
            foreground=INK,
            padding=(9, 8),
            bordercolor=LINE,
            lightcolor=LINE,
            darkcolor=LINE,
            relief="flat",
        )
        style.configure(
            "Primary.TButton",
            background=GREEN,
            foreground=SURFACE,
            padding=(16, 10),
            borderwidth=0,
            relief="flat",
            font=("Segoe UI", 10, "bold"),
        )
        style.map(
            "Primary.TButton",
            background=[("disabled", "#A7B7AE"), ("active", GREEN_HOVER)],
            foreground=[("disabled", SURFACE)],
        )
        style.configure(
            "Quiet.TButton",
            background=BACKGROUND,
            foreground=INK,
            padding=(11, 8),
            borderwidth=0,
            relief="flat",
            font=("Segoe UI", 9, "bold"),
        )
        style.map("Quiet.TButton", background=[("active", MINT)])
        style.configure(
            "Ledger.Treeview",
            background=SURFACE,
            fieldbackground=SURFACE,
            foreground=INK,
            rowheight=39,
            borderwidth=0,
            font=("Segoe UI", 10),
        )
        style.configure(
            "Ledger.Treeview.Heading",
            background="#F6F8F6",
            foreground=MUTED,
            padding=(11, 10),
            relief="flat",
            font=("Segoe UI", 8, "bold"),
        )
        style.map(
            "Ledger.Treeview",
            background=[("selected", MINT)],
            foreground=[("selected", INK)],
        )

    def _build_interface(self) -> None:
        page = ttk.Frame(self.root, style="App.TFrame", padding=(30, 24, 30, 21))
        page.pack(fill="both", expand=True)
        page.columnconfigure(0, weight=1)
        page.rowconfigure(5, weight=1)

        hero = tk.Frame(page, bg=INK, padx=23, pady=18)
        hero.grid(row=0, column=0, sticky="ew")
        brand = tk.Frame(hero, bg=INK)
        brand.pack(fill="x")
        tk.Label(
            brand,
            text="MORROW  /  MONEY NOTES",
            bg=INK,
            fg="#B7D6C4",
            font=("Segoe UI", 9, "bold"),
        ).pack(side="left")
        tk.Label(
            brand,
            text="PRIVATE ON THIS DEVICE",
            bg="#29463D",
            fg="#D8EBD9",
            font=("Segoe UI", 8, "bold"),
            padx=10,
            pady=6,
        ).pack(side="right")
        tk.Label(
            hero,
            text="Know where it went.",
            bg=INK,
            fg=SURFACE,
            font=("Georgia", 25),
        ).pack(anchor="w", pady=(16, 2))
        tk.Label(
            hero,
            text="A clear, local record of your everyday spending.",
            bg=INK,
            fg="#C2D0C9",
            font=("Segoe UI", 10),
        ).pack(anchor="w")

        month_bar = tk.Frame(page, bg=BACKGROUND)
        month_bar.grid(row=1, column=0, sticky="ew", pady=(19, 12))
        month_bar.columnconfigure(0, weight=1)
        tk.Label(
            month_bar,
            text="MONTHLY OVERVIEW",
            bg=BACKGROUND,
            fg=MUTED,
            font=("Segoe UI", 8, "bold"),
        ).grid(row=0, column=0, sticky="w")
        navigation = tk.Frame(month_bar, bg=BACKGROUND)
        navigation.grid(row=0, column=1, rowspan=2, sticky="e")
        ttk.Button(
            navigation, text="Previous", style="Quiet.TButton", command=self.previous_month
        ).pack(side="left", padx=(0, 6))
        tk.Label(
            navigation,
            textvariable=self.month_var,
            bg=BACKGROUND,
            fg=INK,
            font=("Georgia", 14),
            width=17,
            anchor="center",
        ).pack(side="left", padx=5)
        ttk.Button(
            navigation, text="Next", style="Quiet.TButton", command=self.next_month
        ).pack(side="left", padx=(6, 0))

        summary = tk.Frame(page, bg=BACKGROUND)
        summary.grid(row=2, column=0, sticky="ew", pady=(0, 16))
        for column in range(3):
            summary.columnconfigure(column, weight=1, uniform="summary")
        self._build_summary_card(summary, "TOTAL SPENT", self.total_var, 0, accent=GREEN)
        self._build_summary_card(summary, "TRANSACTIONS", self.count_var, 1)
        self._build_summary_card(summary, "TOP CATEGORY", self.top_category_var, 2)

        entry_panel = tk.Frame(
            page,
            bg=SURFACE,
            highlightbackground=LINE,
            highlightthickness=1,
            padx=17,
            pady=13,
        )
        entry_panel.grid(row=3, column=0, sticky="ew", pady=(0, 15))
        entry_panel.columnconfigure(1, weight=2)
        entry_panel.columnconfigure(2, weight=1)
        entry_panel.columnconfigure(3, weight=1)
        tk.Label(
            entry_panel,
            text="ADD AN EXPENSE",
            bg=SURFACE,
            fg=INK,
            font=("Segoe UI", 9, "bold"),
        ).grid(row=0, column=0, columnspan=5, sticky="w", pady=(0, 10))

        self._build_field(entry_panel, "DATE", self.date_var, 0, width=13)
        self._build_field(entry_panel, "DESCRIPTION", self.description_var, 1)
        self._build_category_field(entry_panel, 2)
        self._build_field(entry_panel, "AMOUNT", self.amount_var, 3, width=12)
        self.add_button = ttk.Button(
            entry_panel,
            text="Add expense",
            style="Primary.TButton",
            command=self.add_expense,
        )
        self.add_button.grid(row=2, column=4, sticky="e", padx=(10, 0), pady=(4, 0))
        self.amount_entry.bind("<Return>", lambda _event: self.add_expense())

        content = ttk.Frame(page, style="App.TFrame")
        content.grid(row=5, column=0, sticky="nsew")
        content.columnconfigure(0, weight=7, uniform="content")
        content.columnconfigure(1, weight=3, uniform="content")
        content.rowconfigure(0, weight=1)

        ledger = tk.Frame(
            content,
            bg=SURFACE,
            highlightbackground=LINE,
            highlightthickness=1,
        )
        ledger.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        ledger.columnconfigure(0, weight=1)
        ledger.rowconfigure(1, weight=1)
        ledger_header = tk.Frame(ledger, bg=SURFACE, padx=15, pady=13)
        ledger_header.grid(row=0, column=0, columnspan=2, sticky="ew")
        tk.Label(
            ledger_header,
            text="Transactions",
            bg=SURFACE,
            fg=INK,
            font=("Segoe UI", 12, "bold"),
        ).pack(side="left")
        self.delete_button = ttk.Button(
            ledger_header,
            text="Delete selected",
            style="Quiet.TButton",
            command=self.delete_selected,
            state="disabled",
        )
        self.delete_button.pack(side="right")

        self.tree = ttk.Treeview(
            ledger,
            columns=("date", "description", "category", "amount"),
            show="headings",
            style="Ledger.Treeview",
            selectmode="browse",
        )
        for column, heading in (
            ("date", "DATE"),
            ("description", "DESCRIPTION"),
            ("category", "CATEGORY"),
            ("amount", "AMOUNT"),
        ):
            self.tree.heading(column, text=heading, anchor="w")
        self.tree.column("date", width=94, minwidth=84, anchor="w")
        self.tree.column("description", width=180, minwidth=125, anchor="w")
        self.tree.column("category", width=100, minwidth=85, anchor="w")
        self.tree.column("amount", width=95, minwidth=82, anchor="e")
        self.tree.tag_configure("odd", background="#F8FAF8")
        self.tree.grid(row=1, column=0, sticky="nsew", padx=(10, 0), pady=(0, 10))
        self.scrollbar = ttk.Scrollbar(ledger, orient="vertical", command=self.tree.yview)
        self.scrollbar.grid(row=1, column=1, sticky="ns", padx=(0, 6), pady=(0, 10))
        self.tree.configure(yscrollcommand=self.scrollbar.set)
        self.tree.bind("<<TreeviewSelect>>", self._selection_changed)

        category_panel = tk.Frame(
            content,
            bg=SURFACE,
            highlightbackground=LINE,
            highlightthickness=1,
            padx=16,
            pady=15,
        )
        category_panel.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
        category_panel.columnconfigure(0, weight=1)
        tk.Label(
            category_panel,
            text="By category",
            bg=SURFACE,
            fg=INK,
            font=("Segoe UI", 12, "bold"),
        ).grid(row=0, column=0, sticky="w")
        tk.Label(
            category_panel,
            text="A month at a glance",
            bg=SURFACE,
            fg=MUTED,
            font=("Segoe UI", 9),
        ).grid(row=1, column=0, sticky="w", pady=(3, 14))
        self.category_list = tk.Frame(category_panel, bg=SURFACE)
        self.category_list.grid(row=2, column=0, sticky="new")
        self.category_list.columnconfigure(0, weight=1)

        footer = tk.Frame(page, bg=BACKGROUND)
        footer.grid(row=6, column=0, sticky="ew", pady=(13, 0))
        tk.Label(
            footer,
            textvariable=self.status_var,
            bg=BACKGROUND,
            fg=MUTED,
            font=("Segoe UI", 9),
        ).pack(side="left")
        tk.Label(
            footer,
            text=f"SAVED LOCALLY  /  {self.book.database_path}",
            bg=BACKGROUND,
            fg=MUTED,
            font=("Segoe UI", 8),
        ).pack(side="right")

    def _build_summary_card(
        self, parent: tk.Frame, label: str, variable: tk.StringVar, column: int, accent: str = LINE
    ) -> None:
        card = tk.Frame(
            parent,
            bg=SURFACE,
            highlightbackground=LINE,
            highlightthickness=1,
            padx=16,
            pady=12,
        )
        card.grid(row=0, column=column, sticky="ew", padx=(0 if column == 0 else 5, 5 if column < 2 else 0))
        tk.Label(
            card,
            text=label,
            bg=SURFACE,
            fg=MUTED,
            font=("Segoe UI", 8, "bold"),
        ).pack(anchor="w")
        tk.Label(
            card,
            textvariable=variable,
            bg=SURFACE,
            fg=accent if label == "TOTAL SPENT" else INK,
            font=("Georgia", 19),
        ).pack(anchor="w", pady=(4, 0))

    def _build_field(
        self,
        parent: tk.Frame,
        label: str,
        variable: tk.StringVar,
        column: int,
        width: int | None = None,
    ) -> None:
        field = tk.Frame(parent, bg=SURFACE)
        field.grid(row=1, column=column, sticky="ew", padx=(0, 9))
        tk.Label(
            field,
            text=label,
            bg=SURFACE,
            fg=MUTED,
            font=("Segoe UI", 8, "bold"),
        ).pack(anchor="w", pady=(0, 5))
        entry = ttk.Entry(field, textvariable=variable, style="Field.TEntry", width=width)
        entry.pack(fill="x")
        if label == "AMOUNT":
            self.amount_entry = entry

    def _build_category_field(self, parent: tk.Frame, column: int) -> None:
        field = tk.Frame(parent, bg=SURFACE)
        field.grid(row=1, column=column, sticky="ew", padx=(0, 9))
        tk.Label(
            field,
            text="CATEGORY",
            bg=SURFACE,
            fg=MUTED,
            font=("Segoe UI", 8, "bold"),
        ).pack(anchor="w", pady=(0, 5))
        ttk.Combobox(
            field,
            textvariable=self.category_var,
            values=CATEGORIES,
            state="readonly",
            style="Field.TCombobox",
        ).pack(fill="x")

    def add_expense(self) -> None:
        try:
            spent_on = date.fromisoformat(self.date_var.get().strip())
            amount_cents = amount_to_cents(self.amount_var.get())
            self.book.add(
                spent_on.isoformat(),
                self.description_var.get(),
                self.category_var.get(),
                amount_cents,
            )
        except ValueError as error:
            messagebox.showwarning("Check this expense", str(error), parent=self.root)
            return
        except OSError as error:
            messagebox.showerror("Could not save expense", str(error), parent=self.root)
            return

        self.visible_month = spent_on.replace(day=1)
        self.description_var.set("")
        self.amount_var.set("")
        self.refresh_month()
        self.status_var.set(f"Added {format_amount(amount_cents)} to {spent_on.strftime('%B')}.")
        self.amount_entry.focus_set()

    def previous_month(self) -> None:
        if self.visible_month.month == 1:
            self.visible_month = self.visible_month.replace(
                year=self.visible_month.year - 1, month=12
            )
        else:
            self.visible_month = self.visible_month.replace(month=self.visible_month.month - 1)
        self.refresh_month()

    def next_month(self) -> None:
        if self.visible_month.month == 12:
            self.visible_month = self.visible_month.replace(
                year=self.visible_month.year + 1, month=1
            )
        else:
            self.visible_month = self.visible_month.replace(month=self.visible_month.month + 1)
        self.refresh_month()

    def refresh_month(self) -> None:
        year, month = self.visible_month.year, self.visible_month.month
        self.month_var.set(self.visible_month.strftime("%B %Y"))
        self.expenses = self.book.for_month(year, month)
        total_cents, expense_count = self.book.month_totals(year, month)
        category_totals = self.book.category_totals(year, month)
        self.total_var.set(format_amount(total_cents))
        self.count_var.set(str(expense_count))
        self.top_category_var.set(category_totals[0][0] if category_totals else "None yet")

        for item in self.tree.get_children():
            self.tree.delete(item)
        for index, expense in enumerate(self.expenses):
            self.tree.insert(
                "",
                "end",
                iid=str(expense.id),
                values=(
                    expense.spent_on,
                    expense.description,
                    expense.category,
                    format_amount(expense.amount_cents),
                ),
                tags=("odd",) if index % 2 else (),
            )
        self.delete_button.state(["disabled"])
        self._render_categories(category_totals, total_cents)
        if expense_count == 0:
            self.status_var.set("No expenses recorded for this month yet.")
        else:
            self.status_var.set(f"Showing {expense_count} transaction(s) for {self.month_var.get()}.")

    def _render_categories(self, category_totals: list[tuple[str, int]], total_cents: int) -> None:
        for child in self.category_list.winfo_children():
            child.destroy()

        if not category_totals:
            tk.Label(
                self.category_list,
                text="Category totals will appear here.",
                bg=SURFACE,
                fg=MUTED,
                font=("Segoe UI", 9),
                wraplength=210,
                justify="left",
            ).grid(row=0, column=0, sticky="w", pady=(2, 0))
            return

        for index, (category, amount_cents) in enumerate(category_totals):
            row = tk.Frame(self.category_list, bg=SURFACE)
            row.grid(row=index, column=0, sticky="ew", pady=(0, 12))
            row.columnconfigure(0, weight=1)
            label = tk.Frame(row, bg=SURFACE)
            label.grid(row=0, column=0, sticky="ew")
            tk.Label(
                label,
                text=category,
                bg=SURFACE,
                fg=INK,
                font=("Segoe UI", 9, "bold"),
            ).pack(side="left")
            tk.Label(
                label,
                text=format_amount(amount_cents),
                bg=SURFACE,
                fg=MUTED,
                font=("Segoe UI", 9),
            ).pack(side="right")
            bar = tk.Canvas(
                row,
                height=6,
                bg="#EDF1EE",
                highlightthickness=0,
                bd=0,
            )
            bar.grid(row=1, column=0, sticky="ew", pady=(6, 0))
            bar.update_idletasks()
            width = max(bar.winfo_width(), 160)
            bar.create_rectangle(
                0,
                0,
                width * amount_cents / total_cents,
                6,
                fill=CATEGORY_COLORS[index % len(CATEGORY_COLORS)],
                outline="",
            )

    def _selection_changed(self, _event=None) -> None:
        self.delete_button.state(
            ["!disabled"] if self.tree.selection() else ["disabled"]
        )

    def delete_selected(self) -> None:
        selection = self.tree.selection()
        if not selection:
            return

        expense_id = int(selection[0])
        selected_values = self.tree.item(selection[0], "values")
        description = selected_values[1]
        confirmed = messagebox.askyesno(
            "Delete expense?",
            f"Remove {description!r} ({selected_values[3]}) from your records?",
            parent=self.root,
        )
        if not confirmed:
            return

        if self.book.delete(expense_id):
            self.refresh_month()
            self.status_var.set(f"Removed {description}.")


def main() -> None:
    root = tk.Tk()
    ExpenseTrackerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()