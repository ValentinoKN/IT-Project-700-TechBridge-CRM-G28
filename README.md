# TechBridge MSP CRM

## The quick version

This is Group 28's basic CRM for the ITP700 IT Project. It is made for a fictional small IT support business called **TechBridge MSP**. It lets the team keep companies, contacts, leads, deals and follow-up activities in one place.

Everything in this project is for the class demo only. The users, passwords and customer information are fake. There are no paid APIs, no real emails and no real customer data.

If you just want to run it, do this:

1. Install Git, VS Code and Docker Desktop.
2. Clone this repo in VS Code. Do **not** download a ZIP folder.
3. Start Docker Desktop and wait until it says it is running.
4. Open the VS Code terminal inside the project folder.
5. Run `docker compose up --build`.
6. Go to `http://localhost:8000` and log in.

That is it. The more detailed version is below if you get stuck.

## Project and course details

| Item | Details |
| --- | --- |
| Institution | Richfield Graduate Institute of Technology |
| Module | ITP700 - IT Project |
| Project | TechBridge MSP Customer Relationship Management System |
| Group | Group 28 |
| Main technology | Django, PostgreSQL, Docker and Bootstrap |
| Project type | Fictional small MSP CRM for academic assessment |

## Team and basic ownership

Every person should still understand and contribute to every phase. These are the main areas so the work stays organised and everyone has something clear to show.

| Student | Student number | Main area |
| --- | --- | --- |
| Valentino Naidoo | 402103668 | Team lead, GitHub, Docker, dashboard and final merge |
| Rene Louw | 402309742 | Requirements, forms and document checks |
| Tokelo Mashiane | 402410487 | Companies, contacts and database links |
| Logan Carolus | 402312980 | Leads, deals and list pages |
| Yache Perumal | 402412607 | Roles, validation, activities and permissions |
| Ryan Barnabas | 401510651 | Testing evidence, README and install checks |

## What the system is meant to do

The CRM keeps the basic sales/support work in one simple workflow:

1. Add the company first.
2. Add a contact under that company.
3. Add a lead for the contact and update its status.
4. Convert a good lead into a deal.
5. Log a call, email, meeting or note against a contact or a deal.

There are three roles:

- **Administrator:** can see and manage everything.
- **Manager:** can see and manage all team records.
- **Representative:** only sees records assigned to them.

## Demo logins

| Username | Password | Role |
| --- | --- | --- |
| `admin` | `DemoPass123!` | Administrator |
| `manager` | `DemoPass123!` | Manager |
| `rep` | `DemoPass123!` | Representative |

These accounts are created automatically when the containers start. They are only demo accounts, so please do not use these passwords anywhere else.

## Start from scratch on a new computer

### 1. Install the three things you need

- [Git](https://git-scm.com/downloads) - lets your computer talk to GitHub.
- [Visual Studio Code](https://code.visualstudio.com/) - where you open and edit the project.
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) - runs the app and database without everyone setting them up separately.

When Docker Desktop asks to use **WSL 2**, allow it. If WSL is not installed, open **PowerShell as Administrator** and run:

```powershell
wsl --install
```

Restart the computer when Windows asks. Then open Docker Desktop again and wait for it to finish starting.

### 2. Clone the project into VS Code

1. Open VS Code.
2. Press `Ctrl + Shift + P`.
3. Choose **Git: Clone**.
4. Paste this repository link:

   ```text
   https://github.com/ValentinoKN/IT-Project-700-TechBridge-CRM-G28.git
   ```

5. Choose a normal folder such as Documents.
6. Click **Open** when VS Code asks if you want to open the cloned project.
7. If VS Code asks you to trust the folder, choose **Yes, I trust the authors**.

Cloning means you have a linked working copy. Saving and pushing changes sends them back to GitHub. It is better than downloading a ZIP because a ZIP has no proper team history.

### 3. Run the system

In VS Code, go to **Terminal > New Terminal**. Make sure the terminal path ends in `techbridge-msp-crm`, then run:

```powershell
docker compose up --build
```

The first run can take a few minutes. Docker downloads the free images, builds the Django app, starts PostgreSQL, creates the tables and creates the three demo users.

When you see a line similar to `Starting development server at http://0.0.0.0:8000/`, open:

```text
http://localhost:8000
```

To stop the app, click inside the terminal and press `Ctrl + C`.

## Normal daily use

After the first successful run, open Docker Desktop and use this in the VS Code terminal:

```powershell
docker compose up
```

Use `docker compose up --build` again after changing files such as `requirements.txt`, `Dockerfile` or `docker-compose.yml`. It is also safe to use when you are unsure; it just takes a little longer.

Useful commands:

```powershell
docker compose up --build                     # build and start everything
docker compose up                             # start normally
docker compose down                           # stop the app and database containers
docker compose exec web python manage.py test # run the automated checks
docker compose down -v                        # WARNING: deletes the local demo database
```

The last command wipes only your local Docker database. It is useful if the demo data is broken, but you will lose anything you typed into the app. Run `docker compose up` afterwards and the blank database plus demo logins will be created again.

## How to test it before a demo

Do this basic check as a group before showing the lecturer:

1. Run `docker compose up --build` and log in as `rep`.
2. Add a test company, then add a contact under it.
3. Add a lead, change its status, and convert it to a deal.
4. Add one activity, such as a call or note, linked to the contact or deal.
5. Try the search boxes and CSV export links.
6. Log out and log in as `manager` to confirm managers can see all records.
7. Run the automated tests:

   ```powershell
   docker compose exec web python manage.py test
   ```

Take screenshots of the login, dashboard, a company/contact, a converted deal and the test result. Those are useful as submission evidence.

## What the main files do

| File or folder | What it is for |
| --- | --- |
| `docker-compose.yml` | Starts the web app and PostgreSQL database together. |
| `Dockerfile` | The small recipe Docker uses to build the Django web container. |
| `requirements.txt` | The Python packages the project needs. |
| `config/settings.py` | Project settings, including the database connection and login settings. |
| `crm/models.py` | The database structure: users, companies, contacts, leads, deals and activities. |
| `crm/forms.py` | The add/edit forms and basic form styling. |
| `crm/views.py` | What happens when pages load, save, export or check permissions. |
| `crm/urls.py` | The page links inside the CRM. |
| `crm/tests.py` | Small automated checks for core behaviour and permissions. |
| `crm/management/commands/seed_demo.py` | Creates the class demo logins on startup. |
| `templates/` | The HTML pages the user sees. |

## GitHub in normal words

- **Repo/repository:** the shared project on GitHub.
- **Clone:** make your first linked copy of the repo on your computer.
- **Pull:** get the latest work the team pushed.
- **Branch:** your safe work area for one feature or fix.
- **Commit:** a saved checkpoint with a short message.
- **Push:** send your commits to GitHub.
- **Pull request:** ask for your branch to be checked and added to `main`.
- **Merge:** add approved work into the main version.

## Team Git workflow in VS Code

Before starting any work, pull the newest copy:

```powershell
git checkout main
git pull origin main
```

Make your own branch. Replace the example with your name and task:

```powershell
git checkout -b logan-lead-page
```

Make a small change, run the app and test it. Then save it to GitHub:

```powershell
git status
git add .
git commit -m "Update lead page"
git push -u origin logan-lead-page
```

On GitHub, open a pull request from your branch into `main`. Valentino can check it before merging. This stops one person from accidentally breaking the version everybody else is using.

VS Code also has a **Source Control** icon on the left. You can type a commit message there, click the tick to commit, then use **Sync Changes** to push/pull. The terminal commands above do exactly the same thing and make it easier to see what is happening.

## Common problems and the quick fix

| What you see | What to do |
| --- | --- |
| `docker is not recognized` | Docker Desktop is not installed, or VS Code was opened before it finished installing. Install/open Docker Desktop, then close and reopen VS Code. |
| `docker_engine` or daemon error | Docker Desktop is closed or still starting. Open it and wait until it says it is running. |
| WSL is not installed | Run `wsl --install` in Administrator PowerShell, restart, then reopen Docker Desktop. |
| Port 8000 is already in use | Stop the other terminal/app using port 8000, then run `docker compose up` again. |
| Docker build says access denied around `.deps` | Pull the latest repo first. `.dockerignore` keeps local dependency folders out of the Docker build. Then run `docker compose up --build` again. |
| Login does not work | Run `docker compose down -v`, then `docker compose up`. This resets local demo data and restores the demo users. |

## Keep it safe and simple

Do not put real customer information, real passwords, `.env` files or database backups into GitHub. This project is intentionally local and simple for the assessment. The free Docker setup means any group member can run the same app on their own laptop.
