from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from crm.models import User, Company, Contact, Lead, Deal, Activity


class Command(BaseCommand):
    help = 'Add a small, clearly fictional demonstration without replacing existing records.'

    @transaction.atomic
    def handle(self, *args, **options):
        rep = User.objects.filter(username='rep').first()
        if not rep:
            raise CommandError('Create the local demonstration accounts first.')
        company, _ = Company.objects.get_or_create(name='Cedar IT Demo', defaults={'industry':'IT support', 'email':'office@example.test', 'account_manager':rep})
        contact, _ = Contact.objects.get_or_create(company=company, email='sam@example.test', defaults={'first_name':'Sam','last_name':'Demo','assigned_to':rep})
        Lead.objects.get_or_create(contact=contact, source='Demo website enquiry', defaults={'assigned_to':rep})
        Deal.objects.get_or_create(contact=contact, title='Demo support contract', defaults={'owner':rep, 'stage':'Proposal', 'value':'1500.00'})
        Activity.objects.get_or_create(contact=contact, detail='Fictional call about support requirements.', defaults={'owner':rep,'activity_type':'Call'})
        self.stdout.write('Fictional sample records are ready.')
