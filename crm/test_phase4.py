from datetime import timedelta
from decimal import Decimal
from unittest.mock import patch

from django.db import IntegrityError, transaction
from django.db.models.deletion import ProtectedError
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .forms import CompanyForm, LeadForm
from .models import Activity, Company, Contact, Deal, Lead, User


class Phase4Checks(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.rep = User.objects.create_user(username='rep_a', password='local_test', role='REP')
        cls.other = User.objects.create_user(username='rep_b', password='local_test', role='REP')
        cls.manager = User.objects.create_user(username='manager_test', password='local_test', role='MANAGER')
        cls.admin = User.objects.create_superuser(username='admin_test', password='local_test', role='ADMIN')
        cls.company = Company.objects.create(name='Cedar IT Demo', account_manager=cls.rep)
        cls.contact = Contact.objects.create(company=cls.company, first_name='Sam', last_name='Demo', email='sam@example.test', assigned_to=cls.rep)
        cls.other_company = Company.objects.create(name='Other Demo', account_manager=cls.other)
        cls.other_contact = Contact.objects.create(company=cls.other_company, first_name='Alex', last_name='Other', email='alex@example.test', assigned_to=cls.other)

    def setUp(self):
        self.client.force_login(self.rep)

    def lead(self, **kwargs):
        return Lead.objects.create(contact=self.contact, source='Website', assigned_to=self.rep, **kwargs)

    def test_repeat_conversion_and_source_link(self):
        lead = self.lead()
        for _ in range(2):
            self.client.post(reverse('lead_convert', args=[lead.pk]))
        self.assertEqual(Deal.objects.filter(source_lead=lead).count(), 1)
        lead.refresh_from_db()
        self.assertEqual(lead.status, 'Converted')

    def test_conversion_failure_rolls_back_deal(self):
        lead = self.lead()
        with patch.object(Lead, 'save', side_effect=IntegrityError('simulated failure')):
            response = self.client.post(reverse('lead_convert', args=[lead.pk]))
        lead.refresh_from_db()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(lead.status, 'New')
        self.assertFalse(Deal.objects.exists())

    def test_lost_lead_is_not_converted(self):
        lead = self.lead(status='Lost')
        self.client.post(reverse('lead_convert', args=[lead.pk]))
        self.assertFalse(Deal.objects.exists())

    def test_get_does_not_convert(self):
        lead = self.lead()
        self.client.get(reverse('lead_convert', args=[lead.pk]))
        self.assertFalse(Deal.objects.exists())

    def test_conversion_preserves_owner_and_truncates_title(self):
        self.company.name = 'C' * 120
        self.company.save()
        lead = self.lead()
        self.client.force_login(self.manager)
        response = self.client.post(reverse('lead_convert', args=[lead.pk]))
        deal = Deal.objects.get(source_lead=lead)
        self.assertEqual(deal.owner, self.rep)
        self.assertLessEqual(len(deal.title), 120)
        self.assertRedirects(response, reverse('deal_edit', args=[deal.pk]))

    def test_manual_converted_status_is_invalid(self):
        form = LeadForm(data={'contact': self.contact.pk, 'source': 'Website', 'status': 'Converted', 'assigned_to': self.rep.pk})
        self.assertFalse(form.is_valid())

    def test_converted_status_cannot_be_edited_back(self):
        lead = self.lead(status='Converted')
        form = LeadForm(data={'contact': self.contact.pk, 'source': 'Website', 'status': 'New', 'assigned_to': self.rep.pk}, instance=lead)
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.cleaned_data['status'], 'Converted')

    def test_source_lead_is_unique_in_database(self):
        lead = self.lead()
        Deal.objects.create(contact=self.contact, title='One', owner=self.rep, source_lead=lead)
        with self.assertRaises(IntegrityError), transaction.atomic():
            Deal.objects.create(contact=self.contact, title='Two', owner=self.rep, source_lead=lead)

    def test_company_duplicate_is_rejected_by_database(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            Company.objects.create(name=' cedar IT DEMO ', account_manager=self.rep)

    def test_company_duplicate_has_form_message(self):
        form = CompanyForm(data={'name': ' cedar IT DEMO ', 'account_manager': self.rep.pk})
        self.assertFalse(form.is_valid())
        self.assertIn('already exists', str(form.errors))

    def test_negative_deal_is_rejected_by_database(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            Deal.objects.create(contact=self.contact, title='Invalid', owner=self.rep, value=-1)

    def test_zero_deal_is_allowed(self):
        deal = Deal.objects.create(contact=self.contact, title='Unknown value', owner=self.rep, value=0)
        self.assertEqual(deal.value, 0)

    def test_activity_neither_parent_is_rejected_by_database(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            Activity.objects.create(activity_type='Note', detail='Invalid', owner=self.rep)

    def test_activity_both_parents_is_rejected_by_database(self):
        deal = Deal.objects.create(contact=self.contact, title='Demo', owner=self.rep)
        with self.assertRaises(IntegrityError), transaction.atomic():
            Activity.objects.create(activity_type='Note', detail='Invalid', owner=self.rep, contact=self.contact, deal=deal)

    def test_activity_valid_parent_saves(self):
        item = Activity.objects.create(activity_type='Call', detail='Demo call', owner=self.rep, contact=self.contact)
        self.assertIsNotNone(item.pk)

    def test_fixed_status_check_rejects_unknown_value(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            self.lead(status='Unknown')

    def test_company_with_contacts_cannot_be_deleted(self):
        with self.assertRaises(ProtectedError):
            self.company.delete()
        self.assertTrue(Contact.objects.filter(pk=self.contact.pk).exists())

    def test_manager_cannot_enter_admin_even_if_staff_flag_set(self):
        self.manager.is_staff = True
        self.manager.save()
        self.client.force_login(self.manager)
        response = self.client.get('/admin/')
        self.assertEqual(response.status_code, 302)
        self.assertIn('/admin/login/', response.url)

    def test_administrator_can_enter_admin(self):
        self.client.force_login(self.admin)
        self.assertEqual(self.client.get('/admin/').status_code, 200)

    def test_rep_cannot_submit_foreign_contact(self):
        response = self.client.post(reverse('lead_add'), {'contact': self.other_contact.pk, 'source': 'Website', 'status': 'New', 'assigned_to': self.rep.pk})
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Lead.objects.exists())

    def test_rep_owner_dropdown_contains_only_self(self):
        response = self.client.get(reverse('company_add'))
        self.assertEqual(list(response.context['form'].fields['account_manager'].queryset), [self.rep])

    def test_company_create_edit_and_search(self):
        response = self.client.post(reverse('company_add'), {'name': 'New Demo', 'account_manager': self.rep.pk})
        self.assertEqual(response.status_code, 302)
        company = Company.objects.get(name='New Demo')
        self.client.post(reverse('company_edit', args=[company.pk]), {'name': 'Updated Demo', 'account_manager': self.rep.pk})
        response = self.client.get(reverse('company_list'), {'q': 'Updated'})
        self.assertEqual(list(response.context['companies'].values_list('name', flat=True)), ['Updated Demo'])

    def test_missing_required_contact_does_not_save(self):
        before = Contact.objects.count()
        response = self.client.post(reverse('contact_add'), {'company': self.company.pk, 'first_name': 'Keep me', 'email': 'bad', 'assigned_to': self.rep.pk})
        self.assertEqual(Contact.objects.count(), before)
        self.assertContains(response, 'Keep me')
        self.assertTrue(response.context['form'].errors)

    def test_dashboard_counts_use_role_and_seven_days(self):
        self.lead()
        Lead.objects.create(contact=self.other_contact, source='Referral', assigned_to=self.other)
        for stage, value in [('Proposal', 100), ('Won', 500), ('Lost', 800)]:
            Deal.objects.create(contact=self.contact, title=stage, stage=stage, value=value, owner=self.rep)
        old = Activity.objects.create(contact=self.contact, owner=self.rep, activity_type='Note', detail='Old')
        Activity.objects.filter(pk=old.pk).update(created_at=timezone.now()-timedelta(days=8))
        Activity.objects.create(contact=self.contact, owner=self.rep, activity_type='Call', detail='New')
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.context['lead_total'], 1)
        self.assertEqual(response.context['deal_total'], 3)
        self.assertEqual(response.context['pipeline_value'], Decimal('100'))
        self.assertEqual(response.context['recent_activity_count'], 1)
        self.assertEqual(len(response.context['recent_activities']), 2)

    def test_csv_matches_search_for_all_export_types(self):
        self.lead()
        Deal.objects.create(contact=self.contact, title='Selected proposal', owner=self.rep)
        for kind, term, selected in [('companies', 'Cedar', 'Cedar IT Demo'), ('leads', 'Website', 'Website'), ('deals', 'Selected', 'Selected proposal')]:
            with self.subTest(kind=kind):
                response = self.client.get(reverse('export_csv', args=[kind]), {'q': term})
                self.assertContains(response, selected)
                empty = self.client.get(reverse('export_csv', args=[kind]), {'q': 'no_match_at_all'})
                self.assertEqual(len(empty.content.decode().splitlines()), 1)

    def test_csv_formula_prefix_is_escaped(self):
        Company.objects.create(name='=SUM(1,2)', account_manager=self.rep)
        response = self.client.get(reverse('export_csv', args=['companies']))
        self.assertIn("'=SUM", response.content.decode())
        self.assertNotIn('password', response.content.decode().lower())

    def test_unknown_export_is_not_found(self):
        self.assertEqual(self.client.get(reverse('export_csv', args=['users'])).status_code, 404)

    def test_login_required_and_wrong_password(self):
        self.client.logout()
        self.assertEqual(self.client.get(reverse('dashboard')).status_code, 302)
        response = self.client.post(reverse('login'), {'username': 'rep_a', 'password': 'wrong'})
        self.assertEqual(response.status_code, 200)
        self.assertNotIn('_auth_user_id', self.client.session)

    def test_full_workflow_through_forms(self):
        self.client.post(reverse('company_add'), {'name': 'Workflow Demo', 'account_manager': self.rep.pk})
        company = Company.objects.get(name='Workflow Demo')
        response = self.client.post(reverse('contact_add'), {'company': company.pk, 'first_name': 'Pat', 'last_name': 'Workflow', 'email': 'pat@example.test', 'assigned_to': self.rep.pk})
        self.assertEqual(response.status_code, 302)
        contact = Contact.objects.get(company=company)
        response = self.client.post(reverse('lead_add'), {'contact': contact.pk, 'source': 'Referral', 'status': 'Qualified', 'assigned_to': self.rep.pk})
        self.assertEqual(response.status_code, 302)
        lead = Lead.objects.get(contact=contact)
        self.client.post(reverse('lead_convert', args=[lead.pk]))
        deal = Deal.objects.get(source_lead=lead)
        response = self.client.post(reverse('deal_edit', args=[deal.pk]), {'contact': contact.pk, 'title': 'Workflow proposal', 'stage': 'Proposal', 'value': '2500.00', 'owner': self.rep.pk})
        self.assertEqual(response.status_code, 302)
        deal.refresh_from_db()
        self.assertEqual(deal.value, Decimal('2500.00'))
        response = self.client.post(reverse('activity_add'), {'deal': deal.pk, 'activity_type': 'Call', 'detail': 'Fictional workflow call', 'owner': self.rep.pk})
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Activity.objects.filter(deal=deal, owner=self.rep).exists())
        self.assertContains(self.client.get(reverse('export_csv', args=['deals']), {'q': 'Workflow'}), '2500.00')
