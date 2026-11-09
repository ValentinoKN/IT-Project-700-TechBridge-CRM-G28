from django.core.management.base import BaseCommand, CommandError
from django.db import connection


class Command(BaseCommand):
    help = 'Check older records before applying stricter rules. This never changes records.'

    def handle(self, *args, **options):
        tables = connection.introspection.table_names()
        if 'crm_company' not in tables:
            return
        checks = [
            ('Duplicate company names', 'SELECT COUNT(*) FROM (SELECT LOWER(TRIM(name)) FROM crm_company GROUP BY LOWER(TRIM(name)) HAVING COUNT(*) > 1) duplicates'),
            ('Negative deal values', 'SELECT COUNT(*) FROM crm_deal WHERE value < 0'),
            ('Activities with zero or two links', 'SELECT COUNT(*) FROM crm_activity WHERE (contact_id IS NULL AND deal_id IS NULL) OR (contact_id IS NOT NULL AND deal_id IS NOT NULL)'),
            ('Unknown user roles', "SELECT COUNT(*) FROM crm_user WHERE role NOT IN ('ADMIN','MANAGER','REP')"),
            ('Unknown lead statuses', "SELECT COUNT(*) FROM crm_lead WHERE status NOT IN ('New','Contacted','Qualified','Converted','Lost')"),
            ('Unknown deal stages', "SELECT COUNT(*) FROM crm_deal WHERE stage NOT IN ('Prospecting','Proposal','Negotiation','Won','Lost')"),
            ('Unknown activity types', "SELECT COUNT(*) FROM crm_activity WHERE activity_type NOT IN ('Call','Email','Meeting','Note')"),
        ]
        issues = []
        with connection.cursor() as cursor:
            for label, sql in checks:
                cursor.execute(sql)
                count = cursor.fetchone()[0]
                if count:
                    issues.append(f'{label}: {count}')
            cursor.execute("SELECT COUNT(*) FROM django_migrations WHERE app='crm' AND name='0002_phase4_integrity'")
            if cursor.fetchone()[0]:
                issues.append('This database uses the unpublished Phase 4 migration branch. Keep the backup and reconcile its migration history before upgrading.')
        if issues:
            raise CommandError('Upgrade stopped without changing records. Correct the following in a backed-up copy first: ' + '; '.join(issues))
        self.stdout.write('Existing data checks passed.')
