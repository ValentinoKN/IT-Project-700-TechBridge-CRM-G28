from django import forms
from django.db.models.functions import Lower, Trim
from .models import Activity, Company, Contact, Deal, Lead


class BootstrapForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            # This adds the same Bootstrap look without styling every HTML input by hand.
            field.widget.attrs["class"] = "form-control"


class CompanyForm(BootstrapForm):
    def clean_name(self):
        name = self.cleaned_data["name"].strip()
        existing = Company.objects.annotate(normal_name=Lower(Trim("name"))).filter(normal_name=name.lower())
        if self.instance.pk:
            existing = existing.exclude(pk=self.instance.pk)
        if existing.exists():
            raise forms.ValidationError("A company with this name already exists.")
        return name

    class Meta:
        model = Company
        fields = ["name", "industry", "phone", "email", "account_manager"]


class ContactForm(BootstrapForm):
    class Meta:
        model = Contact
        fields = ["company", "first_name", "last_name", "email", "phone", "assigned_to"]


class LeadForm(BootstrapForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Conversion creates the deal. A normal edit must not skip that step.
        if self.instance.pk and self.instance.status == "Converted":
            self.fields["status"].disabled = True
        else:
            self.fields["status"].choices = [choice for choice in Lead.STATUS_CHOICES if choice[0] != "Converted"]

    class Meta:
        model = Lead
        fields = ["contact", "source", "status", "assigned_to", "notes"]
        widgets = {"notes": forms.Textarea(attrs={"rows": 3})}


class DealForm(BootstrapForm):
    class Meta:
        model = Deal
        fields = ["contact", "title", "stage", "value", "expected_close_date", "owner"]
        widgets = {"expected_close_date": forms.DateInput(attrs={"type": "date"})}


class ActivityForm(BootstrapForm):
    class Meta:
        model = Activity
        fields = ["contact", "deal", "activity_type", "detail", "owner"]
        widgets = {"detail": forms.Textarea(attrs={"rows": 3})}
