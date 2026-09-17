from django.test import TestCase
from django.urls import reverse
from .models import Company, Contact, Lead, User


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

