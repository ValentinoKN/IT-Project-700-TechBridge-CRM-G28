# TechBridge MSP CRM

A simple Customer Relationship Management system for the ITP700 Group 28 project. It uses Django, PostgreSQL, Docker and Bootstrap. All data is fictional and there are no paid APIs.

## What the system does

- Users log in as an Administrator, Manager or Representative.
- Stores companies and their linked contacts.
- Tracks leads from New to Contacted, Qualified, Converted or Lost.
- Converts a lead into a deal.
- Tracks deals, values and expected closing dates.
- Logs calls, emails, meetings and notes.
- Shows a basic dashboard and exports companies, leads and deals to CSV.
- Representatives can only open records assigned to them. Managers and administrators can view all records.

## First-time setup in VS Code

Do not download a ZIP file. Each person clones the repository once, which makes a linked local working folder.

1. Install [Git](https://git-scm.com/downloads), [Docker Desktop](https://www.docker.com/products/docker-desktop/) and [VS Code](https://code.visualstudio.com/).
2. Open VS Code and press `Ctrl + Shift + P`.
3. Select **Git: Clone** and paste:

   ```text
   https://github.com/ValentinoKN/IT-Project-700-TechBridge-CRM-G28.git
   ```

4. Choose a folder, then click **Open** when VS Code asks.
5. Make sure Docker Desktop is running.
6. In VS Code choose **Terminal > New Terminal** and run:

   ```powershell
   docker compose up --build
   ```

7. Open `http://localhost:8000` in your browser.

The first run downloads the free Docker images, creates the PostgreSQL database and adds demo users. Later, use `docker compose up` only. Stop the system with `Ctrl + C`.

## Demo login details

| User | Password | Role |
| --- | --- | --- |
| `admin` | `DemoPass123!` | Administrator |
| `manager` | `DemoPass123!` | Manager |
| `rep` | `DemoPass123!` | Representative |

These are only for the class demo. Do not use them in a real system.

## Daily GitHub workflow

Before starting work, open the VS Code terminal and get the latest work:

```powershell
git checkout main
git pull origin main
```

Make your own branch. Use your name and feature:

```powershell
git checkout -b tokelo-company-contact
```

Make your changes, run the system, then save them to GitHub:

```powershell
git add .
git commit -m "Add company contact validation"
git push -u origin tokelo-company-contact
```

Open GitHub and create a pull request from your branch into `main`. Valentino checks the work before merging it. Do not work directly on `main`.

## Basic Git words

- **Repository / repo:** the project and its history on GitHub.
- **Clone:** make the first linked copy of the repo on your laptop.
- **Branch:** your own work area, separate from the main version.
- **Commit:** a saved checkpoint with a message explaining the change.
- **Push:** send your commits from your computer to GitHub.
- **Pull:** get the latest team changes from GitHub.
- **Pull request:** asks for your branch to be checked and merged into `main`.
- **Merge:** adds approved work into the main version.

## Useful commands

```powershell
docker compose up --build       # first run after code changes
docker compose up               # normal run
docker compose down             # stop containers
docker compose down -v          # stop and erase local demo database
docker compose exec web python manage.py test  # run tests
```

Never upload passwords for real users, `.env` files, database backups or real customer data to GitHub.

## Suggested responsibilities

- Valentino: GitHub, Docker, final merge and dashboard.
- Rene: requirements, forms and documentation checks.
- Tokelo: companies, contacts and database relations.
- Logan: leads, deals and dashboard list pages.
- Yache: roles, validation, activities and permissions.
- Ryan: testing evidence, README and install checks.
