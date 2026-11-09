# TechBridge MSP CRM

Group 28's ITP700 project for a fictional IT support business. We keep companies,
contacts, leads, deals and follow-up notes in one place.

## Run the Windows demo

Download the Windows application ZIP from the Phase 5 handover, choose **Extract All**,
and open **TechBridgeCRM.exe**. Keep its `_internal` folder beside it. You do not need
Python or Docker for this package. It works offline after download.

Choose a password on the first run. Log in as `admin`, `manager` or `rep` with that
password. Open `http://127.0.0.1:8000`. Keep the application window open and press
Ctrl+C there to stop it. See [Windows instructions](INSTALL_WINDOWS.txt).

The Windows demo uses SQLite on one computer. The PostgreSQL/Docker source option
below keeps the original Phase 4 setup. Each option has its own database.

## Basic workflow

1. Add a company and then its contact.
2. Add a lead and record its source.
3. Convert it to a deal, then update the value and stage.
4. Log a call, email, meeting or note against one contact or deal.
5. Check the dashboard, search or export Companies, Leads or Deals to CSV.

Admins and managers see all business records. Representatives see assigned records.
Only an administrator with staff access manages users. Email activities are notes;
this app does not send emails or take payments.

## Run from source with PostgreSQL

Install and start Docker Desktop with Compose. Download or clone this repository.
Copy `.env.example` to `.env` and replace all `CHANGE_ME` values. Keep `.env` private.
From the project folder run:

```powershell
docker compose up --build
```

Open `http://127.0.0.1:8000`. Use `admin`, `manager` or `rep` and your `DEMO_PASSWORD`.
The first build needs internet. Later offline starts require the images and packages
to have been downloaded already. Stop with Ctrl+C, then `docker compose down`.
**Do not add `-v`: that deletes the database volume.**

## Data and backups

The Windows demo saves to `%LOCALAPPDATA%\TechBridgeCRM`. Stop it and run `Backup.cmd`.
Use `Restore.cmd` only to replace records with a selected backup; it saves the current
database first. Keep a backup in a separate private location too.

Docker saves PostgreSQL data in a named volume. See [developer notes](docs/DEVELOPMENT.md)
for source setup, tests, backup/restore and building the EXE.

## If it does not start

Extract the entire ZIP, close other TechBridge windows and check port 8000 is free.
Do not disable antivirus for a warning. Send the exact message to the group.
For Docker, check `.env` and that Docker Desktop is running.

## Project status

See [verification](docs/PHASE5_VERIFICATION.md) for actual checks and limitations.
Both modes are local assessment demos, not public production deployments. Use
fictional records. Second-computer acceptance is recorded separately.
Private member guides and correspondence are not kept in this repository.
