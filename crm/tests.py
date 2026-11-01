from django.test import TestCase
from django.urls import reverse
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction

from .models import Activity, Company, Contact, Lead, User


class CrmTests(TestCase):
    def setUp(self):
        self.rep_one = User.objects.create_user(username="repone", password="testpass", role=User.REPRESENTATIVE)
        self.rep_two = User.objects.create_user(username="reptwo", password="testpass", role=User.REPRESENTATIVE)
        company = Company.objects.create(name="Demo Co", account_manager=self.rep_one)
        self.contact = Contact.objects.create(company=company, first_name="Sam", last_name="Demo", email="sam@example.com", assigned_to=self.rep_one)

    def test_lead_converts_to_deal(self):
        lead = Lead.objects.create(contact=self.contact, source="Website", assigned_to=self.rep_one)
        self.client.login(username="repone", password="testpass")
        response = self.client.post(reverse("lead_convert", args=[lead.id]))
        lead.refresh_from_db()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(lead.status, "Converted")
        self.assertEqual(lead.contact.deals.count(), 1)

    def test_representative_cannot_open_other_users_lead(self):
        lead = Lead.objects.create(contact=self.contact, source="Website", assigned_to=self.rep_one)
        self.client.login(username="reptwo", password="testpass")
        self.assertEqual(self.client.get(reverse("lead_edit", args=[lead.id])).status_code, 404)

    def test_representative_export_only_contains_their_leads(self):
        Lead.objects.create(contact=self.contact, source="Website", assigned_to=self.rep_one)
        other_company = Company.objects.create(name="Other Co", account_manager=self.rep_two)
        other_contact = Contact.objects.create(company=other_company, first_name="Alex", last_name="Other", email="alex@example.com", assigned_to=self.rep_two)
        Lead.objects.create(contact=other_contact, source="Referral", assigned_to=self.rep_two)
        self.client.login(username="repone", password="testpass")

        response = self.client.get(reverse("export_csv", args=["leads"]))

        self.assertEqual(response.status_code, 200)
        self.assertIn("sam demo", response.content.decode().lower())
        self.assertNotIn("alex other", response.content.decode().lower())

    def test_activity_needs_one_linked_record(self):
        activity = Activity(activity_type="Call", detail="Quick check-in", owner=self.rep_one)

        with self.assertRaisesMessage(ValidationError, "Choose one linked contact or one linked deal."):
            activity.full_clean()

    def test_company_form_rejects_same_name_with_different_case_and_spaces(self):
        self.client.login(username="repone", password="testpass")

        response = self.client.post(reverse("company_add"), {"name": "  demo co  ", "account_manager": self.rep_one.id})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "A company with this name already exists.")
        self.assertEqual(Company.objects.count(), 1)

    def test_company_can_keep_its_own_name_when_edited(self):
        company = self.contact.company
        self.client.login(username="repone", password="testpass")

        response = self.client.post(reverse("company_edit", args=[company.id]), {"name": "Demo Co", "industry": "IT support", "account_manager": self.rep_one.id})

        company.refresh_from_db()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(company.industry, "IT support")

    def test_database_rejects_duplicate_company_name(self):
        # This skips the form on purpose to show the database rule works on its own.
        with self.assertRaises(IntegrityError), transaction.atomic():
            Company.objects.create(name=" demo co ", account_manager=self.rep_two)
