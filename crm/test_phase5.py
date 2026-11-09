from django.core.management import call_command
from django.core.management.base import CommandError
from django.db import connection
from django.test import TestCase, Client
from django.urls import reverse
from .models import User, Company, Contact


class HandoverChecks(TestCase):
    def setUp(self):
        self.rep = User.objects.create_user(username='rep', password='A-long-local-test-password', role='REP')
        self.other = User.objects.create_user(username='other', password='A-long-local-test-password', role='REP')
        self.company = Company.objects.create(name='Example Demo', account_manager=self.rep)

    def test_logout_closes_session(self):
        self.client.force_login(self.rep)
        self.assertEqual(self.client.post(reverse('logout')).status_code, 302)
        self.assertRedirects(self.client.get(reverse('company_list')), '/login/?next=/companies/')

    def test_password_is_hashed(self):
        self.assertNotEqual(self.rep.password, 'A-long-local-test-password')
        self.assertTrue(self.rep.check_password('A-long-local-test-password'))

    def test_csrf_required_for_record_changes(self):
        browser = Client(enforce_csrf_checks=True)
        browser.force_login(self.rep)
        response = browser.post(reverse('company_add'), {'name':'Forged', 'account_manager':self.rep.pk})
        self.assertEqual(response.status_code, 403)
        self.assertFalse(Company.objects.filter(name='Forged').exists())

    def test_direct_company_contact_and_deal_urls_are_blocked(self):
        from .models import Deal
        contact = Contact.objects.create(company=self.company, first_name='Sample', last_name='Contact', email='a@example.test', assigned_to=self.rep)
        deal = Deal.objects.create(contact=contact, title='Sample deal', owner=self.rep)
        self.client.force_login(self.other)
        for route, record in [('company_edit',self.company),('contact_edit',contact),('deal_edit',deal)]:
            self.assertEqual(self.client.get(reverse(route,args=[record.pk])).status_code,404)

    def test_offline_assets_are_local(self):
        page = self.client.get(reverse('login')).content.decode()
        self.assertIn('/static/vendor/bootstrap.min.css',page)
        self.assertIn('/static/vendor/bootstrap.bundle.min.js',page)
        self.assertNotIn('cdn.jsdelivr.net',page)

    def test_sample_data_is_repeatable(self):
        call_command('sample_data',verbosity=0)
        counts = {name: model.objects.count() for name,model in [('companies',Company),('contacts',Contact)]}
        call_command('sample_data',verbosity=0)
        self.assertEqual(counts, {'companies':Company.objects.count(),'contacts':Contact.objects.count()})

    def test_existing_data_preflight(self):
        call_command('check_data',verbosity=0)

    def test_staff_admin_cannot_skip_lead_conversion(self):
        from django.contrib import admin
        from .models import Lead
        form = admin.site._registry[Lead].form()
        self.assertNotIn('Converted', [value for value, label in form.fields['status'].choices])
