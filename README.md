# Python Mini Projects

A growing collection of small, practical Python projects. Each project is designed to solve a real problem, practice a useful skill, or explore how AI can make everyday tools more helpful.

## Projects

Projects will be added here as they are built. Each project should have its own folder with its code and a README explaining what it does and how to run it.

| Project | What it does | Topics |
| --- | --- | --- |
| [File Organizer](projects/file-organizer/) | Sort files into folders by extension with a desktop preview before moving anything. | Python, GUI, files |

## Run the File Organizer

Install Python 3 with Tkinter, then run the app from the repository root:

```bash
python projects/file-organizer/app.py
```

The app opens a desktop window. Choose a source folder, review the preview, then confirm to move files. It uses only the Python standard library. See the [File Organizer README](projects/file-organizer/README.md) for details and test instructions.

## Git Branch Workflow

Create a branch for your changes. This keeps them separate from `main`:

```bash
git switch -c feature/file-organizer-ui
```

Stage the files you changed and commit with a short description:

```bash
git add README.md projects/file-organizer
git commit -m "feat: add desktop file organizer"
```

Push the branch to GitHub:

```bash
git push -u origin feature/file-organizer-ui
```

To merge locally after the branch is committed, switch to `main`, update it, merge, and push:

```bash
git switch main
git pull origin main
git merge --no-ff feature/file-organizer-ui
git push origin main
git branch -d feature/file-organizer-ui
```

You can also merge the branch through a pull request on GitHub instead of running `git merge` locally.

## Project Ideas

Some ideas for future projects:

- **File organizer**: sort files into folders by type or date.
- **Expense tracker**: record spending and summarize monthly totals.
- **Study helper**: create flashcards and quiz yourself from notes.
- **AI text summarizer**: turn long text into concise notes using an AI model.
- **AI email drafter**: generate a first draft from a short description.

AI projects may use an external model or API. Their individual READMEs will explain setup, required packages, and any API keys needed. Never commit passwords, API keys, or other secrets to the repository.


## Project Principles

- Keep projects small, focused, and practical.
- Include clear run instructions and dependency information.
- Prefer readable code and explain non-obvious decisions.
- For AI features, describe what data is sent to external services and provide a useful fallback where practical.