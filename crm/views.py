import csv
from datetime import timedelta
from django.db import DatabaseError, transaction
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Sum
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from .forms import ActivityForm, CompanyForm, ContactForm, DealForm, LeadForm
from .models import Activity, Company, Contact, Deal, Lead, User

RECENT_DAYS = 7
RECENT_LIMIT = 5
SEARCH_FIELDS = {
    "companies": ["name", "industry", "email"],
    "leads": ["contact__first_name", "contact__last_name", "source", "status"],
    "deals": ["title", "contact__first_name", "contact__last_name", "stage"],
}


def own_or_all(user, queryset, owner_field):
    # Reps only get their own records. Managers/admins get the full list. This is the main access rule.
    return queryset if user.can_manage_all else queryset.filter(**{owner_field: user})


def allow_record(user, record, owner_name):
    if not user.can_manage_all and getattr(record, owner_name) != user:
        raise Http404("Record not found")


def list_context(request, queryset, search_fields):
    # One tiny reusable search helper keeps all list pages working the same way.
    term = request.GET.get("q", "").strip()
    if term:
        condition = Q()
        for field in search_fields:
            condition |= Q(**{f"{field}__icontains": term})
        queryset = queryset.filter(condition)
    return queryset, term


def limit_form_choices(form, user):
    """Keep dropdowns in line with the same role rules used by the pages."""
    if user.can_manage_all:
        return form
    for field in ["account_manager", "assigned_to", "owner"]:
        if field in form.fields:
            form.fields[field].queryset = User.objects.filter(pk=user.pk)
            form.fields[field].initial = user
    if "company" in form.fields:
        form.fields["company"].queryset = Company.objects.filter(Q(account_manager=user) | Q(pk=form.instance.company_id))
    if "contact" in form.fields:
        form.fields["contact"].queryset = Contact.objects.filter(assigned_to=user)
    if "deal" in form.fields:
        form.fields["deal"].queryset = Deal.objects.filter(owner=user)
    return form


@login_required
def dashboard(request):
    leads = own_or_all(request.user, Lead.objects.all(), "assigned_to")
    deals = own_or_all(request.user, Deal.objects.all(), "owner")
    activities = own_or_all(request.user, Activity.objects.all(), "owner")
    return render(request, "crm/dashboard.html", {
        "lead_total": leads.count(),
        "deal_total": deals.count(),
        "recent_activity_count": activities.filter(created_at__gte=timezone.now() - timedelta(days=RECENT_DAYS)).count(),
        "open_deal_total": deals.exclude(stage__in=["Won", "Lost"]).count(),
        "pipeline_value": deals.exclude(stage__in=["Won", "Lost"]).aggregate(total=Sum("value"))["total"] or 0,
        "recent_activities": activities.select_related("owner", "contact", "deal")[:RECENT_LIMIT],
    })


@login_required
def company_list(request):
    companies = own_or_all(request.user, Company.objects.all(), "account_manager")
    companies, term = list_context(request, companies, SEARCH_FIELDS["companies"])
    return render(request, "crm/company_list.html", {"companies": companies, "term": term})


@login_required
def company_form(request, pk=None):
    company = get_object_or_404(Company, pk=pk) if pk else None
    if company:
        allow_record(request.user, company, "account_manager")
    form = limit_form_choices(CompanyForm(request.POST or None, instance=company), request.user)
    if form.is_valid():
        saved = form.save(commit=False)
        if not request.user.can_manage_all:
            # A rep cannot quietly assign a new company to somebody else using the form.
            saved.account_manager = request.user
        saved.save()
        messages.success(request, "Company saved.")
        return redirect("company_list")
    return render(request, "crm/form.html", {"form": form, "title": "Edit company" if company else "Add company"})


@login_required
def contact_list(request):
    contacts = own_or_all(request.user, Contact.objects.select_related("company", "assigned_to"), "assigned_to")
    contacts, term = list_context(request, contacts, ["first_name", "last_name", "company__name", "email"])
    return render(request, "crm/contact_list.html", {"contacts": contacts, "term": term})


@login_required
def contact_form(request, pk=None):
    contact = get_object_or_404(Contact, pk=pk) if pk else None
    if contact:
        allow_record(request.user, contact, "assigned_to")
    form = limit_form_choices(ContactForm(request.POST or None, instance=contact), request.user)
    if form.is_valid():
        saved = form.save(commit=False)
        if not request.user.can_manage_all:
            saved.assigned_to = request.user
        saved.save()
        messages.success(request, "Contact saved.")
        return redirect("contact_list")
    return render(request, "crm/form.html", {"form": form, "title": "Edit contact" if contact else "Add contact"})


@login_required
def lead_list(request):
    leads = own_or_all(request.user, Lead.objects.select_related("contact", "assigned_to"), "assigned_to")
    leads, term = list_context(request, leads, SEARCH_FIELDS["leads"])
    return render(request, "crm/lead_list.html", {"leads": leads, "term": term})


@login_required
def lead_form(request, pk=None):
    lead = get_object_or_404(Lead, pk=pk) if pk else None
    if lead:
        allow_record(request.user, lead, "assigned_to")
    form = limit_form_choices(LeadForm(request.POST or None, instance=lead), request.user)
    if form.is_valid():
        saved = form.save(commit=False)
        if not request.user.can_manage_all:
            saved.assigned_to = request.user
        saved.save()
        messages.success(request, "Lead saved.")
        return redirect("lead_list")
    return render(request, "crm/form.html", {"form": form, "title": "Edit lead" if lead else "Add lead"})


@login_required
def convert_lead(request, pk):
    lead = get_object_or_404(Lead, pk=pk)
    allow_record(request.user, lead, "assigned_to")
    if request.method != "POST":
        return redirect("lead_list")
    try:
        with transaction.atomic():
            # Lock the lead before checking it again. PostgreSQL serialises two clicks here.
            lead = get_object_or_404(Lead.objects.select_for_update(), pk=pk)
            allow_record(request.user, lead, "assigned_to")
            if lead.status == "Converted" or Deal.objects.filter(source_lead=lead).exists():
                messages.info(request, "This lead has already been converted.")
                return redirect("lead_list")
            if lead.status == "Lost":
                messages.info(request, "Lost leads cannot be converted.")
                return redirect("lead_list")
            deal = Deal.objects.create(
                contact=lead.contact,
                source_lead=lead,
                title=f"{lead.contact.company.name} ({lead.source})"[:120],
                owner=lead.assigned_to,
            )
            lead.status = "Converted"
            lead.save(update_fields=["status"])
    except DatabaseError:
        messages.error(request, "This lead could not be converted; no changes were saved. Please try again.")
        return redirect("lead_list")
    messages.success(request, "Lead converted to a deal.")
    return redirect("deal_edit", pk=deal.pk)


@login_required
def deal_list(request):
    deals = own_or_all(request.user, Deal.objects.select_related("contact", "owner"), "owner")
    deals, term = list_context(request, deals, SEARCH_FIELDS["deals"])
    return render(request, "crm/deal_list.html", {"deals": deals, "term": term})


@login_required
def deal_form(request, pk=None):
    deal = get_object_or_404(Deal, pk=pk) if pk else None
    if deal:
        allow_record(request.user, deal, "owner")
    form = limit_form_choices(DealForm(request.POST or None, instance=deal), request.user)
    if form.is_valid():
        saved = form.save(commit=False)
        if not request.user.can_manage_all:
            saved.owner = request.user
        saved.save()
        messages.success(request, "Deal saved.")
        return redirect("deal_list")
    return render(request, "crm/form.html", {"form": form, "title": "Edit deal" if deal else "Add deal"})


@login_required
def activity_list(request):
    activities = own_or_all(request.user, Activity.objects.select_related("owner", "contact", "deal"), "owner")
    return render(request, "crm/activity_list.html", {"activities": activities})


@login_required
def activity_form(request):
    form = limit_form_choices(ActivityForm(request.POST or None), request.user)
    if form.is_valid():
        saved = form.save(commit=False)
        if not request.user.can_manage_all:
            saved.owner = request.user
        saved.save()
        messages.success(request, "Activity logged.")
        return redirect("activity_list")
    return render(request, "crm/form.html", {"form": form, "title": "Log activity"})


def csv_cell(value):
    # Keep formula-leading text as text when opened in a spreadsheet.
    if isinstance(value, str) and value.lstrip().startswith(("=", "+", "-", "@", "＝", "＋", "－", "＠")):
        return "'" + value
    if isinstance(value, str) and value.startswith(("\t", "\r", "\n")):
        return "'" + value
    return value


@login_required
def export_csv(request, record_type):
    config = {
        "companies": (Company, "account_manager", ["Name", "Industry", "Phone", "Email", "Account manager", "Created"]),
        "leads": (Lead, "assigned_to", ["Contact", "Company", "Source", "Status", "Assigned to", "Created"]),
        "deals": (Deal, "owner", ["Title", "Contact", "Company", "Stage", "Value (R)", "Expected close date", "Owner"]),
    }
    if record_type not in config:
        raise Http404("Unknown export")
    model, owner_field, headers = config[record_type]
    rows = own_or_all(request.user, model.objects.all(), owner_field)
    rows, term = list_context(request, rows, SEARCH_FIELDS[record_type])
    response = HttpResponse(content_type="text/csv; charset=utf-8")
    response["Content-Disposition"] = f'attachment; filename="techbridge_{record_type}_{timezone.localdate().isoformat()}.csv"'
    writer = csv.writer(response)
    writer.writerow(headers)
    for item in rows:
        if record_type == "companies":
            values = [item.name, item.industry, item.phone, item.email, item.account_manager.username, timezone.localtime(item.created_at).strftime("%d/%m/%Y")]
        elif record_type == "leads":
            values = [str(item.contact), item.contact.company.name, item.source, item.status, item.assigned_to.username, timezone.localtime(item.created_at).strftime("%d/%m/%Y")]
        else:
            values = [item.title, str(item.contact), item.contact.company.name, item.stage, f"{item.value:.2f}", item.expected_close_date.strftime("%d/%m/%Y") if item.expected_close_date else "", item.owner.username]
        writer.writerow([csv_cell(value) for value in values])
    return response
