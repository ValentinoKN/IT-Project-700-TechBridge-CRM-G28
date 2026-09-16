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

### Get the project from GitHub

1. Open PowerShell where you want to keep the project.
2. Download the code:

   ```powershell
   git clone https://github.com/ValentinoKN/IT-Project-700-TechBridge-CRM-G28.git
   cd IT-Project-700-TechBridge-CRM-G28
   ```

3. Follow the **Run it on your computer** steps above.

### Make your own changes

Do not edit directly on the `main` branch. Make a branch, commit your work, push it, then ask the team to check it. Before you start, download any changes the team already pushed:

```powershell
git checkout main
git pull origin main
```

```powershell
git checkout -b rene-customer-page
git add .
git commit -m "Add customer page"
git push -u origin rene-customer-page
```

On GitHub, open a pull request from your branch into `main`. Valentino can check it and merge it when it works. Keep commits small and use clear messages so everyone can see who did what.

## Suggested first jobs

- Valentino: project setup, dashboard and final merge
- Rene: customer form and validation
- Tokelo: ticket form and validation
- Logan: simple CSS and page layout
- Yache: testing checklist and test data
- Ryan: README and installation screenshots
