# File Organizer

A small desktop app for sorting files into folders named after their extensions. It scans only the selected folder, not its subfolders. Files without an extension go into `No extension`.

The app uses Python's standard library and Tkinter. It previews every move before changing anything, asks for confirmation, and chooses a numbered filename if a destination already contains a file with the same name.

## Start the App

From this folder, run:

```bash
python app.py
```

Choose a source folder and, if needed, a destination folder. Review the preview, then select **Organize files** and confirm. The default destination is an `Organized` folder inside the source folder.

## Run the Tests

```bash
python -m unittest
```