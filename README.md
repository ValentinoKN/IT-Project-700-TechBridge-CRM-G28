# TechBridge MSP CRM

A small beginner-friendly CRM for the ITP700 group project. It runs on a laptop using Flask and SQLite, so there are no paid APIs or cloud services needed.

## What it does now

- Add and view customers
- Add and view support tickets
- Change a ticket status
- See simple totals on the dashboard

## Run it on your computer

1. Install Python 3.10 or newer.
2. Open a terminal in this project folder.
3. Create a virtual environment:

   ```powershell
   py -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

4. Install the packages:

   ```powershell
   pip install -r requirements.txt
   ```

5. Start the app:

   ```powershell
   python app.py
   ```

6. Open `http://127.0.0.1:5000` in your browser.

The `crm.db` database file is created automatically. It is not uploaded to GitHub because every member can start with a clean database.

## Working from VS Code and GitHub

Do not download the project as a ZIP file. Each person should **clone** it once in VS Code. Cloning makes a local working folder that is linked to this GitHub repository.

### First setup in VS Code

1. Install [Git](https://git-scm.com/downloads), [Python](https://www.python.org/downloads/) and [Visual Studio Code](https://code.visualstudio.com/).
2. Open VS Code.
3. Press `Ctrl + Shift + P`, choose **Git: Clone**, then paste this link:

   ```text
   https://github.com/ValentinoKN/IT-Project-700-TechBridge-CRM-G28.git
   ```

4. Choose a folder on your laptop and click **Open** when VS Code asks.
5. In VS Code, open **Terminal > New Terminal** and run:

   ```powershell
   py -m venv .venv
   .\.venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   python app.py
   ```

6. Open `http://127.0.0.1:5000` in your browser. Stop the app with `Ctrl + C` in the terminal.

### Before you start work

Always get the newest team work first. In the VS Code terminal, run:

```powershell
git checkout main
git pull origin main
```

Then make your own branch. Use your name and the thing you are doing:

```powershell
git checkout -b rene-customer-page
```

### Save and send your changes

Make your changes in VS Code. Test the app. Then use the Source Control icon on the left of VS Code, or run these commands:

```powershell
git add .
git commit -m "Add customer page"
git push -u origin rene-customer-page
```

After pushing, open GitHub. Create a pull request from your branch into `main`. Valentino checks that it works before merging it. This makes it clear what each person worked on.

### Important Git words

- **Repository (repo):** the project folder on GitHub with its full history.
- **Clone:** make the first linked copy of the repo on your laptop. It is not a ZIP download.
- **Main:** the main working version of the project. Do not change it directly.
- **Branch:** your own safe copy of the work, for example `logan-page-layout`.
- **Commit:** a saved checkpoint with a short message saying what you changed.
- **Push:** send your committed work from your laptop to GitHub.
- **Pull:** bring the latest team work from GitHub onto your laptop.
- **Pull request:** a request to add your branch work into `main` after somebody checks it.
- **Merge:** add an approved pull request into `main`.

### Basic rules for the group

- Pull before you start.
- Work on your own branch.
- Test before pushing.
- Commit small changes with clear messages.
- Never upload the `crm.db` file or `.venv` folder.

## Suggested first jobs

- Valentino: project setup, dashboard and final merge
- Rene: customer form and validation
- Tokelo: ticket form and validation
- Logan: simple CSS and page layout
- Yache: testing checklist and test data
- Ryan: README and installation screenshots
