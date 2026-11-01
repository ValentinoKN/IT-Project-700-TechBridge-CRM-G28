from django.test import TestCase
from django.urls import reverse
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.db.models import ProtectedError

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

    def test_contact_gets_created_date_automatically(self):
        self.assertIsNotNone(self.contact.created_at)

    def test_company_with_contacts_cannot_be_deleted(self):
        company = self.contact.company

        with self.assertRaises(ProtectedError):
            company.delete()

        self.assertTrue(Company.objects.filter(pk=company.pk).exists())
        self.assertTrue(Contact.objects.filter(pk=self.contact.pk).exists())

    def test_valid_contact_saves(self):
        self.client.login(username="repone", password="testpass")

        response = self.client.post(reverse("contact_add"), {"company": self.contact.company.id, "first_name": "Lee", "last_name": "New", "email": "lee@example.com", "assigned_to": self.rep_one.id})

        self.assertEqual(response.status_code, 302)
        self.assertTrue(Contact.objects.filter(email="lee@example.com").exists())

    def test_invalid_contact_shows_errors_and_keeps_typed_values(self):
        self.client.login(username="repone", password="testpass")

        response = self.client.post(reverse("contact_add"), {"company": self.contact.company.id, "first_name": "", "last_name": "Typed", "email": "not-an-email", "assigned_to": self.rep_one.id})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "This field is required.")
        self.assertContains(response, "Enter a valid email address.")
        self.assertContains(response, 'value="Typed"')
        self.assertEqual(Contact.objects.count(), 1)

    def test_representative_cannot_add_contact_to_another_reps_company(self):
        # The company ID is sent by hand, as if someone edited the page to get around the dropdown.
        self.client.login(username="reptwo", password="testpass")

        response = self.client.post(reverse("contact_add"), {"company": self.contact.company.id, "first_name": "Lee", "last_name": "New", "email": "lee@example.com", "assigned_to": self.rep_two.id})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Select a valid choice.")
        self.assertEqual(Contact.objects.count(), 1)

    def test_representative_can_keep_company_someone_else_manages_when_editing_contact(self):
        other_company = Company.objects.create(name="Other Co", account_manager=self.rep_two)
        contact = Contact.objects.create(company=other_company, first_name="Alex", last_name="Other", email="alex@example.com", assigned_to=self.rep_one)
        self.client.login(username="repone", password="testpass")

        response = self.client.post(reverse("contact_edit", args=[contact.id]), {"company": other_company.id, "first_name": "Alex", "last_name": "Other", "email": "alex@example.com", "phone": "0821234567", "assigned_to": self.rep_one.id})

        contact.refresh_from_db()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(contact.phone, "0821234567")
