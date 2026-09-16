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

## GitHub workflow for the group

Do not edit directly on the `main` branch. Make a branch, commit your work, push it, then ask the team to check it.

```powershell
git checkout -b your-name-feature
git add .
git commit -m "Add customer page"
git push -u origin your-name-feature
```

## Suggested first jobs

- Valentino: project setup, dashboard and final merge
- Rene: customer form and validation
- Tokelo: ticket form and validation
- Logan: simple CSS and page layout
- Yache: testing checklist and test data
- Ryan: README and installation screenshots

