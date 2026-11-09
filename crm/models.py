from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.functions import Lower, Trim
from django.core.validators import MinValueValidator
from django.utils import timezone


class User(AbstractUser):
    ADMIN = "ADMIN"
    MANAGER = "MANAGER"
    REPRESENTATIVE = "REP"
    ROLE_CHOICES = [(ADMIN, "Administrator"), (MANAGER, "Manager"), (REPRESENTATIVE, "Representative")]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default=REPRESENTATIVE)

    class Meta(AbstractUser.Meta):
        constraints = [
            models.CheckConstraint(
                condition=models.Q(role__in=["ADMIN", "MANAGER", "REP"]),
                name="valid_user_role",
            ),
        ]

    @property
    def can_manage_all(self):
        # One simple role check used by the views instead of repeating the same if statement everywhere.
        return self.role in [self.ADMIN, self.MANAGER]


class Company(models.Model):
    name = models.CharField(max_length=120, unique=True)
    industry = models.CharField(max_length=80, blank=True)
    phone = models.CharField(max_length=30, blank=True)
    email = models.EmailField(blank=True)
    # PROTECT means we do not accidentally remove a user while their company records still exist.
    account_manager = models.ForeignKey(User, on_delete=models.PROTECT, related_name="companies")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]
        constraints = [models.UniqueConstraint(Lower(Trim("name")), name="unique_company_name_ignoring_case", violation_error_message="A company with this name already exists.")]

    def __str__(self):
        return self.name


class Contact(models.Model):
    company = models.ForeignKey(Company, on_delete=models.PROTECT, related_name="contacts")
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField()
    phone = models.CharField(max_length=30, blank=True)
    assigned_to = models.ForeignKey(User, on_delete=models.PROTECT, related_name="contacts")

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["last_name", "first_name"]

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Lead(models.Model):
    STATUS_CHOICES = [("New", "New"), ("Contacted", "Contacted"), ("Qualified", "Qualified"), ("Converted", "Converted"), ("Lost", "Lost")]
    contact = models.ForeignKey(Contact, on_delete=models.PROTECT, related_name="leads")
    source = models.CharField(max_length=80)
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default="New")
    assigned_to = models.ForeignKey(User, on_delete=models.PROTECT, related_name="leads")
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(status__in=["New", "Contacted", "Qualified", "Converted", "Lost"]),
                name="valid_lead_status",
            ),
        ]

    def __str__(self):
        return f"{self.contact} - {self.status}"


class Deal(models.Model):
    STAGE_CHOICES = [("Prospecting", "Prospecting"), ("Proposal", "Proposal"), ("Negotiation", "Negotiation"), ("Won", "Won"), ("Lost", "Lost")]
    contact = models.ForeignKey(Contact, on_delete=models.PROTECT, related_name="deals")
    title = models.CharField(max_length=120)
    stage = models.CharField(max_length=15, choices=STAGE_CHOICES, default="Prospecting")
    value = models.DecimalField(max_digits=12, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    source_lead = models.OneToOneField(Lead, on_delete=models.PROTECT, null=True, blank=True, related_name="converted_deal", editable=False)
    expected_close_date = models.DateField(null=True, blank=True)
    owner = models.ForeignKey(User, on_delete=models.PROTECT, related_name="deals")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(stage__in=["Prospecting", "Proposal", "Negotiation", "Won", "Lost"]),
                name="valid_deal_stage",
            ),
            models.CheckConstraint(condition=models.Q(value__gte=0), name="deal_value_not_negative"),
        ]

    def __str__(self):
        return self.title


class Activity(models.Model):
    TYPE_CHOICES = [("Call", "Call"), ("Email", "Email"), ("Meeting", "Meeting"), ("Note", "Note")]
    contact = models.ForeignKey(Contact, on_delete=models.PROTECT, related_name="activities", null=True, blank=True)
    deal = models.ForeignKey(Deal, on_delete=models.PROTECT, related_name="activities", null=True, blank=True)
    activity_type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    detail = models.TextField()
    owner = models.ForeignKey(User, on_delete=models.PROTECT, related_name="activities")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(activity_type__in=["Call", "Email", "Meeting", "Note"]),
                name="valid_activity_type",
            ),
            models.CheckConstraint(
                condition=(
                    models.Q(contact__isnull=False, deal__isnull=True)
                    | models.Q(contact__isnull=True, deal__isnull=False)
                ),
                name="activity_one_parent",
            ),
        ]

    def clean(self):
        # An activity must be about one thing. Both blank or both selected makes the record confusing.
        if bool(self.contact_id) == bool(self.deal_id):
            raise ValidationError("Choose one linked contact or one linked deal.")
