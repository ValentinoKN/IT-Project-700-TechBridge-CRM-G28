import csv
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Sum
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from .forms import ActivityForm, CompanyForm, ContactForm, DealForm, LeadForm
from .models import Activity, Company, Contact, Deal, Lead


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
    if "company" in form.fields:
        form.fields["company"].queryset = Company.objects.filter(account_manager=user)
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
        "open_deal_total": deals.exclude(stage__in=["Won", "Lost"]).count(),
        "pipeline_value": deals.exclude(stage__in=["Won", "Lost"]).aggregate(total=Sum("value"))["total"] or 0,
        "recent_activities": activities.select_related("owner", "contact", "deal")[:6],
    })


@login_required
def company_list(request):
    companies = own_or_all(request.user, Company.objects.all(), "account_manager")
    companies, term = list_context(request, companies, ["name", "industry", "email"])
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
    leads, term = list_context(request, leads, ["contact__first_name", "contact__last_name", "source", "status"])
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
    if request.method != "POST" or lead.status == "Converted":
        return redirect("lead_list")
    # Converting creates a basic deal first, so the team can edit title/value/stage after conversion.
    Deal.objects.create(contact=lead.contact, title=f"Deal for {lead.contact}", owner=lead.assigned_to)
    lead.status = "Converted"
    lead.save(update_fields=["status"])
    messages.success(request, "Lead converted to a deal.")
    return redirect("deal_list")


@login_required
def deal_list(request):
    deals = own_or_all(request.user, Deal.objects.select_related("contact", "owner"), "owner")
    deals, term = list_context(request, deals, ["title", "contact__first_name", "contact__last_name", "stage"])
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


@login_required
def export_csv(request, record_type):
    # CSV is plain spreadsheet-friendly text. It is enough for the project export requirement.
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = f'attachment; filename="{record_type}.csv"'
    writer = csv.writer(response)
    if record_type == "companies":
        writer.writerow(["Company", "Industry", "Email", "Manager"])
        for item in own_or_all(request.user, Company.objects.select_related("account_manager"), "account_manager"):
            writer.writerow([item.name, item.industry, item.email, item.account_manager.username])
    elif record_type == "leads":
        writer.writerow(["Contact", "Source", "Status", "Owner"])
        for item in own_or_all(request.user, Lead.objects.select_related("contact", "assigned_to"), "assigned_to"):
            writer.writerow([str(item.contact), item.source, item.status, item.assigned_to.username])
    elif record_type == "deals":
        writer.writerow(["Deal", "Contact", "Stage", "Value", "Owner"])
        for item in own_or_all(request.user, Deal.objects.select_related("contact", "owner"), "owner"):
            writer.writerow([item.title, str(item.contact), item.stage, item.value, item.owner.username])
    else:
        raise Http404("Unknown export")
    return response
