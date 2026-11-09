"""Local Windows demonstration launcher. Business code stays in the crm app."""
import argparse
import getpass
import json
import os
from pathlib import Path
import secrets
import shutil
import socket
import sqlite3
import sys
import threading
import time
import webbrowser
from datetime import datetime
from contextlib import closing


def data_folder(value=None):
    return Path(value) if value else Path(os.environ.get('LOCALAPPDATA', Path.home())) / 'TechBridgeCRM'


def backup_database(database, folder):
    folder.mkdir(parents=True, exist_ok=True)
    target = folder / ('techbridge-' + datetime.now().strftime('%Y%m%d-%H%M%S-%f') + '.sqlite3')
    with closing(sqlite3.connect(database)) as source, closing(sqlite3.connect(target)) as dest:
        source.backup(dest)
        if dest.execute('PRAGMA integrity_check').fetchone()[0] != 'ok':
            raise RuntimeError('The backup did not pass the integrity check.')
    return target


def restore_database(source, database):
    source = Path(source).resolve()
    if source == database.resolve():
        raise ValueError('Choose a backup file, not the current database.')
    with closing(sqlite3.connect(source.as_uri() + '?mode=ro', uri=True)) as con:
        if con.execute('PRAGMA integrity_check').fetchone()[0] != 'ok':
            raise ValueError('This backup is damaged.')
        tables = {row[0] for row in con.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        if not {'crm_user', 'crm_company', 'crm_deal', 'django_migrations'} <= tables:
            raise ValueError('This is not a TechBridge database backup.')
    saved = backup_database(database, database.parent / 'backups') if database.exists() else None
    staged = database.with_suffix('.restore')
    shutil.copy2(source, staged)
    os.replace(staged, database)
    return saved


def main():
    parser = argparse.ArgumentParser(description='TechBridge CRM local Windows demo')
    parser.add_argument('--data-dir', help='Optional separate local data folder')
    parser.add_argument('--port', type=int, default=8000)
    parser.add_argument('--no-browser', action='store_true')
    parser.add_argument('--init-only', action='store_true')
    parser.add_argument('--backup', action='store_true')
    parser.add_argument('--restore', metavar='BACKUP_FILE')
    parser.add_argument('--sample-data', action='store_true', help='Add a few fictional demo records')
    args = parser.parse_args()
    folder = data_folder(args.data_dir).resolve()
    folder.mkdir(parents=True, exist_ok=True)
    database = folder / 'crm.sqlite3'
    # A second start or restore must not change a database that is in use.
    lock = open(folder / 'app.lock', 'a+b')
    lock.seek(0); lock.write(b'0'); lock.flush(); lock.seek(0)
    if os.name == 'nt':
        import msvcrt
        try:
            msvcrt.locking(lock.fileno(), msvcrt.LK_NBLCK, 1)
        except OSError:
            raise RuntimeError('TechBridge is already using this data folder. Close its window first.')
    if args.backup:
        if not database.exists():
            raise ValueError('There is no database to back up yet. Start the application first.')
        print('Backup saved:', backup_database(database, folder / 'backups'))
        return
    if args.restore:
        if input('Replace current records with this backup? Type RESTORE to continue: ') != 'RESTORE':
            print('Restore cancelled.'); return
        print('Previous database backup:', restore_database(args.restore, database))
        print('Restore complete. Start TechBridge normally to apply any newer migrations.')
        return
    settings_file = folder / 'local-settings.json'
    if not settings_file.exists():
        settings_file.write_text(json.dumps({'secret_key': secrets.token_urlsafe(50)}), encoding='utf-8')
    secret = json.loads(settings_file.read_text(encoding='utf-8'))['secret_key']
    os.environ.update(DJANGO_SETTINGS_MODULE='config.settings', USE_SQLITE='1',
                      SQLITE_PATH=str(database), SECRET_KEY=secret, DEBUG='0')
    import django
    django.setup()
    from django.core.management import call_command
    from django.contrib.auth.password_validation import validate_password
    from django.core.exceptions import ValidationError
    from crm.models import User
    if database.exists():
        backup = backup_database(database, folder / 'backups')
        print('Safety copy:', backup)
    call_command('check_data', verbosity=0)
    call_command('migrate', interactive=False, verbosity=0)
    if not User.objects.exists():
        print('First run: choose a password for the three local demonstration accounts.')
        password = os.environ.get('TECHBRIDGE_SETUP_PASSWORD')
        if password is None:
            while True:
                password = getpass.getpass('Password (at least 10 characters): ')
                if password != getpass.getpass('Repeat password: '):
                    print('The passwords did not match.'); continue
                try:
                    validate_password(password)
                    if len(password) < 10:
                        raise ValidationError('Use at least 10 characters.')
                    break
                except ValidationError as exc:
                    print('; '.join(exc.messages))
        if len(password) < 10:
            raise ValueError('The setup password must have at least 10 characters.')
        os.environ['DEMO_PASSWORD'] = password
        call_command('seed_demo', verbosity=0)
        os.environ.pop('DEMO_PASSWORD', None)
        print('Usernames: admin, manager, rep. Each starts with the password you just chose.')
    if args.sample_data:
        call_command('sample_data', verbosity=0)
    print('Data folder:', folder)
    print('Mode: local SQLite demonstration. PostgreSQL/Docker is a separate source setup.')
    if args.init_only:
        print('Initialisation complete.'); return
    from django.core.wsgi import get_wsgi_application
    from waitress import create_server
    server = create_server(get_wsgi_application(), host='127.0.0.1', port=args.port, threads=4)
    url = 'http://127.0.0.1:' + str(args.port)
    print('Open', url, flush=True)
    print('Keep this window open. Press Ctrl+C here to stop.', flush=True)
    if not args.no_browser:
        threading.Timer(1, lambda: webbrowser.open(url)).start()
    try:
        server.run()
    except KeyboardInterrupt:
        print('\nStopping TechBridge.')
    finally:
        server.close()
        lock.close()


if __name__ == '__main__':
    try:
        main()
    except Exception as exc:
        print('TechBridge could not complete this action:', exc, file=sys.stderr, flush=True)
        if sys.stdin.isatty():
            try:
                input('Press Enter to close. ')
            except EOFError:
                pass
        sys.exit(1)
