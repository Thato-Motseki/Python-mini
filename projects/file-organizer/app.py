from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from organizer import PlannedMove, category_for, move_files, plan_moves


BACKGROUND = "#F3F6F3"
SURFACE = "#FFFFFF"
INK = "#19251F"
MUTED = "#718077"
LINE = "#DCE5DE"
GREEN = "#176B53"
GREEN_HOVER = "#105640"
MINT = "#E5F2EB"
AMBER = "#F0B84B"


class FileOrganizerApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Tidy | File Organizer")
        self.root.geometry("1040x740")
        self.root.minsize(820, 640)
        self.root.configure(background=BACKGROUND)

        self.source_var = tk.StringVar()
        self.destination_var = tk.StringVar()
        self.destination_custom = False
        self.setting_destination = False
        self.moves: list[PlannedMove] = []

        self.destination_var.trace_add("write", self._destination_edited)
        self._configure_styles()
        self._build_interface()

    def _configure_styles(self) -> None:
        style = ttk.Style(self.root)
        style.theme_use("clam")
        style.configure("App.TFrame", background=BACKGROUND)
        style.configure("Surface.TFrame", background=SURFACE)
        style.configure(
            "Path.TEntry",
            fieldbackground=SURFACE,
            foreground=INK,
            insertcolor=GREEN,
            padding=(11, 10),
            bordercolor=LINE,
            lightcolor=LINE,
            darkcolor=LINE,
            relief="flat",
        )
        style.configure(
            "Browse.TButton",
            background=SURFACE,
            foreground=INK,
            padding=(15, 9),
            bordercolor=LINE,
            relief="flat",
            font=("Segoe UI", 10, "bold"),
        )
        style.map(
            "Browse.TButton",
            background=[("active", MINT)],
            bordercolor=[("active", GREEN)],
        )
        style.configure(
            "Accent.TButton",
            background=GREEN,
            foreground=SURFACE,
            padding=(19, 11),
            borderwidth=0,
            relief="flat",
            font=("Segoe UI", 10, "bold"),
        )
        style.map(
            "Accent.TButton",
            background=[("disabled", "#A9B8AE"), ("active", GREEN_HOVER)],
            foreground=[("disabled", SURFACE)],
        )
        style.configure(
            "Quiet.TButton",
            background=BACKGROUND,
            foreground=INK,
            padding=(14, 10),
            borderwidth=0,
            relief="flat",
            font=("Segoe UI", 10, "bold"),
        )
        style.map("Quiet.TButton", background=[("active", MINT)])
        style.configure(
            "Preview.Treeview",
            background=SURFACE,
            fieldbackground=SURFACE,
            foreground=INK,
            rowheight=39,
            borderwidth=0,
            font=("Segoe UI", 10),
        )
        style.configure(
            "Preview.Treeview.Heading",
            background="#F6F8F6",
            foreground=MUTED,
            padding=(12, 11),
            relief="flat",
            font=("Segoe UI", 9, "bold"),
        )
        style.map(
            "Preview.Treeview",
            background=[("selected", MINT)],
            foreground=[("selected", INK)],
        )

    def _build_interface(self) -> None:
        page = ttk.Frame(self.root, style="App.TFrame", padding=(34, 25, 34, 22))
        page.pack(fill="both", expand=True)

        header = tk.Frame(page, bg=BACKGROUND)
        header.pack(fill="x")

        brand = tk.Frame(header, bg=BACKGROUND)
        brand.pack(side="left")
        mark = tk.Label(
            brand,
            text="T",
            bg=GREEN,
            fg=SURFACE,
            font=("Georgia", 15, "bold"),
            width=2,
            height=1,
            padx=2,
            pady=3,
        )
        mark.pack(side="left", padx=(0, 10))
        tk.Label(
            brand,
            text="TIDY  /  FILE ORGANIZER",
            bg=BACKGROUND,
            fg=INK,
            font=("Segoe UI", 10, "bold"),
        ).pack(side="left")

        tk.Label(
            header,
            text="LOCAL FILES ONLY",
            bg=MINT,
            fg=GREEN,
            font=("Segoe UI", 8, "bold"),
            padx=11,
            pady=7,
        ).pack(side="right", pady=2)

        hero = tk.Frame(page, bg=BACKGROUND)
        hero.pack(fill="x", pady=(28, 23))
        tk.Label(
            hero,
            text="A little room to breathe.",
            bg=BACKGROUND,
            fg=INK,
            font=("Georgia", 27),
        ).pack(anchor="w")
        tk.Label(
            hero,
            text="Sort a folder by file type. Nothing moves until you say so.",
            bg=BACKGROUND,
            fg=MUTED,
            font=("Segoe UI", 11),
        ).pack(anchor="w", pady=(7, 0))

        folders = ttk.Frame(page, style="App.TFrame")
        folders.pack(fill="x", pady=(0, 19))
        folders.columnconfigure(0, weight=1, uniform="folder")
        folders.columnconfigure(1, weight=1, uniform="folder")
        self._build_folder_picker(
            folders, "SOURCE FOLDER", self.source_var, self._choose_source, 0
        )
        self._build_folder_picker(
            folders,
            "DESTINATION FOLDER",
            self.destination_var,
            self._choose_destination,
            1,
        )

        self.file_count_var = tk.StringVar(value="--")
        self.type_count_var = tk.StringVar(value="--")
        stats = tk.Frame(
            page,
            bg=SURFACE,
            highlightbackground=LINE,
            highlightthickness=1,
        )
        stats.pack(fill="x", pady=(0, 22))
        stats.columnconfigure((0, 1, 2), weight=1, uniform="stat")
        self._build_stat(stats, "FILES TO SORT", self.file_count_var, 0)
        self._build_stat(stats, "FILE TYPES", self.type_count_var, 1)
        self._build_stat(stats, "MODE", "Safe preview", 2)
        for column in (1, 2):
            tk.Frame(stats, bg=LINE, width=1).grid(
                row=0, column=column, sticky="ns", pady=13
            )

        preview_header = tk.Frame(page, bg=BACKGROUND)
        preview_header.pack(fill="x", pady=(0, 10))
        tk.Label(
            preview_header,
            text="Move preview",
            bg=BACKGROUND,
            fg=INK,
            font=("Segoe UI", 13, "bold"),
        ).pack(side="left")
        self.preview_note = tk.Label(
            preview_header,
            text="Choose a folder to get started",
            bg=BACKGROUND,
            fg=MUTED,
            font=("Segoe UI", 9),
        )
        self.preview_note.pack(side="right")

        table = tk.Frame(
            page,
            bg=SURFACE,
            highlightbackground=LINE,
            highlightthickness=1,
        )
        table.pack(fill="both", expand=True)
        table.columnconfigure(0, weight=1)
        table.rowconfigure(0, weight=1)

        self.empty_state = tk.Frame(table, bg=SURFACE)
        self.empty_state.grid(row=0, column=0, sticky="nsew")
        self.empty_title = tk.Label(
            self.empty_state,
            text="Choose a source folder",
            bg=SURFACE,
            fg=INK,
            font=("Georgia", 17),
        )
        self.empty_title.pack(pady=(63, 6))
        self.empty_message = tk.Label(
            self.empty_state,
            text="Your move preview will appear here.",
            bg=SURFACE,
            fg=MUTED,
            font=("Segoe UI", 10),
        )
        self.empty_message.pack()

        self.tree = ttk.Treeview(
            table,
            columns=("file", "type", "destination"),
            show="headings",
            style="Preview.Treeview",
        )
        self.tree.heading("file", text="FILE NAME", anchor="w")
        self.tree.heading("type", text="TYPE", anchor="w")
        self.tree.heading("destination", text="NEW LOCATION", anchor="w")
        self.tree.column("file", width=285, minwidth=145, anchor="w")
        self.tree.column("type", width=125, minwidth=90, anchor="w")
        self.tree.column("destination", width=430, minwidth=190, anchor="w")
        self.tree.tag_configure("odd", background="#FAFCFA")

        self.scrollbar = ttk.Scrollbar(table, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=self.scrollbar.set)
        self.tree.grid(row=0, column=0, sticky="nsew")
        self.scrollbar.grid(row=0, column=1, sticky="ns")
        self.tree.grid_remove()
        self.scrollbar.grid_remove()

        footer = tk.Frame(page, bg=BACKGROUND)
        footer.pack(fill="x", pady=(18, 0))
        self.status_var = tk.StringVar(value="Ready when you are.")
        tk.Label(
            footer,
            textvariable=self.status_var,
            bg=BACKGROUND,
            fg=MUTED,
            font=("Segoe UI", 9),
        ).pack(side="left", fill="x", expand=True, anchor="w")
        ttk.Button(
            footer,
            text="Refresh preview",
            style="Quiet.TButton",
            command=self.refresh_preview,
        ).pack(side="right", padx=(8, 0))
        self.organize_button = ttk.Button(
            footer,
            text="Organize files",
            style="Accent.TButton",
            command=self.organize_files,
            state="disabled",
        )
        self.organize_button.pack(side="right")

    def _build_folder_picker(
        self,
        parent: ttk.Frame,
        label: str,
        variable: tk.StringVar,
        command,
        column: int,
    ) -> None:
        section = tk.Frame(parent, bg=BACKGROUND)
        section.grid(row=0, column=column, sticky="ew", padx=(0, 12 if column == 0 else 0))
        tk.Label(
            section,
            text=label,
            bg=BACKGROUND,
            fg=MUTED,
            font=("Segoe UI", 8, "bold"),
        ).pack(anchor="w", pady=(0, 7))
        controls = ttk.Frame(section, style="App.TFrame")
        controls.pack(fill="x")
        controls.columnconfigure(0, weight=1)
        ttk.Entry(controls, textvariable=variable, style="Path.TEntry").grid(
            row=0, column=0, sticky="ew", padx=(0, 8)
        )
        ttk.Button(
            controls,
            text="Browse",
            style="Browse.TButton",
            command=command,
        ).grid(row=0, column=1)

    def _build_stat(self, parent: tk.Frame, label: str, value, column: int) -> None:
        cell = tk.Frame(parent, bg=SURFACE)
        cell.grid(row=0, column=column, sticky="nsew", padx=18, pady=13)
        tk.Label(
            cell,
            text=label,
            bg=SURFACE,
            fg=MUTED,
            font=("Segoe UI", 8, "bold"),
        ).pack(anchor="w")
        tk.Label(
            cell,
            textvariable=value if isinstance(value, tk.StringVar) else None,
            text=value if isinstance(value, str) else None,
            bg=SURFACE,
            fg=INK,
            font=("Segoe UI", 13, "bold"),
        ).pack(anchor="w", pady=(3, 0))

    def _destination_edited(self, *_args) -> None:
        if not self.setting_destination:
            self.destination_custom = True

    def _set_default_destination(self, path: Path) -> None:
        self.setting_destination = True
        self.destination_var.set(str(path))
        self.setting_destination = False
        self.destination_custom = False

    def _choose_source(self) -> None:
        selected = filedialog.askdirectory(parent=self.root, title="Choose a source folder")
        if not selected:
            return
        self.source_var.set(selected)
        if not self.destination_custom:
            self._set_default_destination(Path(selected) / "Organized")
        self.refresh_preview()

    def _choose_destination(self) -> None:
        current = self.destination_var.get().strip()
        initial_dir = current if Path(current).is_dir() else str(Path.home())
        selected = filedialog.askdirectory(
            parent=self.root,
            title="Choose a destination folder",
            initialdir=initial_dir,
        )
        if selected:
            self.destination_var.set(selected)
            self.destination_custom = True
            self.refresh_preview()

    def refresh_preview(self) -> None:
        source_text = self.source_var.get().strip()
        destination_text = self.destination_var.get().strip()
        if not source_text:
            self.moves = []
            self._update_counts()
            self._show_empty(
                "Choose a source folder", "Your move preview will appear here."
            )
            self.status_var.set("Ready when you are.")
            self.organize_button.state(["disabled"])
            return

        source_dir = Path(source_text).expanduser()
        if not source_dir.is_dir():
            self.moves = []
            self._show_empty("Folder not found", "Choose an existing source folder to continue.")
            self.status_var.set("The source folder could not be found.")
            self._update_counts()
            self.organize_button.state(["disabled"])
            return

        if not destination_text:
            self._set_default_destination(source_dir / "Organized")
            destination_text = self.destination_var.get()

        destination_dir = Path(destination_text).expanduser()
        try:
            self.moves = plan_moves(source_dir, destination_dir)
        except OSError as error:
            self.moves = []
            self._show_empty("Could not read this folder", str(error))
            self.status_var.set("Preview unavailable.")
            self._update_counts()
            self.organize_button.state(["disabled"])
            return

        self._update_counts()
        if not self.moves:
            self._show_empty("All clear.", "No files to organize in this folder.")
            self.preview_note.configure(text="Nothing to move")
            self.status_var.set("No files to organize.")
            self.organize_button.state(["disabled"])
            return

        self._show_table()
        self.preview_note.configure(
            text=f"{len(self.moves)} file(s)  /  {len({category_for(move.source) for move in self.moves})} type(s)"
        )
        for index, move in enumerate(self.moves):
            relative_destination = move.destination.relative_to(destination_dir)
            self.tree.insert(
                "",
                "end",
                values=(move.source.name, category_for(move.source), str(relative_destination)),
                tags=("odd",) if index % 2 else (),
            )
        self.status_var.set("Preview ready. Your files have not been moved.")
        self.organize_button.state(["!disabled"])

    def _update_counts(self) -> None:
        self.file_count_var.set(f"{len(self.moves):02d}")
        self.type_count_var.set(
            f"{len({category_for(move.source) for move in self.moves}):02d}"
        )

    def _clear_table(self) -> None:
        for item in self.tree.get_children():
            self.tree.delete(item)

    def _show_empty(self, title: str, message: str) -> None:
        self._clear_table()
        self.tree.grid_remove()
        self.empty_state.grid()
        self.empty_title.configure(text=title)
        self.empty_message.configure(text=message)
        self.preview_note.configure(text="Choose a folder to get started")

    def _show_table(self) -> None:
        self._clear_table()
        self.empty_state.grid_remove()
        self.tree.grid()
        self.scrollbar.grid()

    def organize_files(self) -> None:
        if not self.moves:
            return

        destination = self.destination_var.get().strip()
        file_count = len(self.moves)
        confirmed = messagebox.askyesno(
            "Organize these files?",
            f"Move {file_count} file(s) into:\n\n{destination}\n\n"
            "Existing files will not be replaced.",
            parent=self.root,
        )
        if not confirmed:
            return

        try:
            move_files(self.moves)
        except OSError as error:
            messagebox.showerror("Could not finish organizing", str(error), parent=self.root)
            self.refresh_preview()
            return

        self.refresh_preview()
        self.status_var.set(f"Done. Organized {file_count} file(s).")


def main() -> None:
    root = tk.Tk()
    FileOrganizerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()