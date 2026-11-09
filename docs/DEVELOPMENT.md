# Working on TechBridge

The business code is in `crm/`. Models hold the database rules, forms validate input,
views check access and handle actions, and templates display the result. `desktop.py`
is only the portable startup/backup wrapper. The SQLite demo and PostgreSQL source
mode use the same CRM code. They do not share a database automatically.

## Source setup on Windows

Install Python 3.12 x64 from the official Python distribution. In the project folder:

```powershell
py -3.12 -m venv .venv
.venv\Scripts\python -m pip install -r requirements-lock.txt
.venv\Scripts\python desktop.py
```

The launcher creates local SQLite data under `%LOCALAPPDATA%\TechBridgeCRM` and asks
for a password on first run. Do not set a real password in a committed script.
For a separate fictional practice database:

```powershell
.venv\Scripts\python desktop.py --data-dir .\practice-data --sample-data
```

Keep that practice directory out of version control. The source setup needs internet
to install packages; the portable release ZIP already contains its runtime.

## Tests

```powershell
$env:USE_SQLITE = '1'
.venv\Scripts\python manage.py test crm --verbosity 2
.venv\Scripts\python manage.py check
.venv\Scripts\python manage.py makemigrations --check --dry-run
```

For PostgreSQL tests use a local test server, unset USE_SQLITE and set POSTGRES_HOST,
POSTGRES_PORT, POSTGRES_DB, POSTGRES_USER and POSTGRES_PASSWORD. The database user needs
permission to create the isolated Django test database. Never point test scripts at
someone else's live data. The test suite creates and destroys its test database.

## PostgreSQL with Docker

Follow README.md and replace all placeholders in `.env.example` when making `.env`.
Compose runs the data preflight, migrations, demo-user setup and static collection,
then starts Waitress. It exposes only 127.0.0.1:8000. PostgreSQL stays inside the
Compose network. `docker compose down` retains the named database volume; `down -v`
removes it and must not be used for an ordinary stop.

## PostgreSQL backup and separate restore

The following commands use the default database/user names from `.env.example`.
Adjust the names if your local settings differ. Do not overwrite a working database.
The Docker command path still needs independent installation verification.

```powershell
New-Item -ItemType Directory -Force backups
docker compose exec -T db pg_dump -U techbridge -d techbridge_crm -Fc -f /tmp/techbridge.dump
docker compose cp db:/tmp/techbridge.dump ./backups/techbridge.dump
docker compose exec -T db createdb -U techbridge techbridge_restore_check
docker compose cp ./backups/techbridge.dump db:/tmp/restore-check.dump
docker compose exec -T db pg_restore -U techbridge --exit-on-error -d techbridge_restore_check /tmp/restore-check.dump
docker compose exec -T db psql -U techbridge -d techbridge_restore_check -c "SELECT count(*) FROM crm_company;"
```

Use a new dated filename for later backups. If the restore-check database already
exists, choose another empty database name; do not drop existing data automatically.
Keep backups private and copy selected backups to another device.

## Building the Windows package

Build on Windows x64 using Python 3.12. Install the runtime lock file, then:

```powershell
.venv\Scripts\python -m pip install pyinstaller==6.22.3
# Run the commands in build_windows.ps1 using the activated .venv.
.venv\Scripts\Activate.ps1
.\build_windows.ps1
```

Do not weaken PowerShell policy to run the helper; its commands can be run manually
with `.venv\Scripts\python` if script execution is restricted. Distribute the complete
`dist/TechBridgeCRM` folder, not just the EXE. Add INSTALL_WINDOWS.txt, Backup.cmd,
Restore.cmd and Add sample records.cmd. Include dependency licences and the source
revision/manifest. Test the resulting ZIP after extracting it to a new directory.

## Migration history

Tokelo's 0002, 0003 and 0004 migrations are preserved. 0005 adds the remaining design
rules. Do not renumber or delete applied migrations. The data preflight stops invalid
legacy records without deleting them. Back up and correct records before retrying.
The unpublished local 0002_phase4_integrity branch is not this migration history;
its databases require a reviewed reconciliation rather than faking migrations.

## Limits

This is a local academic demo. Public production use needs a separate security and
deployment review, including HTTPS, abuse protection, auditing and backup operations.
SQLite does not have PostgreSQL row-level SELECT FOR UPDATE locking. Use the
PostgreSQL path for demonstrating that concurrency behaviour. Keep secrets, user
databases, private learning notes and correspondence out of this repository.
