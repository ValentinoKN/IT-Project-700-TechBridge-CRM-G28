from django.contrib.auth import views as auth_views
from django.urls import path
from . import views

urlpatterns = [
    path("login/", auth_views.LoginView.as_view(template_name="registration/login.html"), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("", views.dashboard, name="dashboard"),
    path("companies/", views.company_list, name="company_list"),
    path("companies/add/", views.company_form, name="company_add"),
    path("companies/<int:pk>/edit/", views.company_form, name="company_edit"),
    path("contacts/", views.contact_list, name="contact_list"),
    path("contacts/add/", views.contact_form, name="contact_add"),
    path("contacts/<int:pk>/edit/", views.contact_form, name="contact_edit"),
    path("leads/", views.lead_list, name="lead_list"),
    path("leads/add/", views.lead_form, name="lead_add"),
    path("leads/<int:pk>/edit/", views.lead_form, name="lead_edit"),
    path("leads/<int:pk>/convert/", views.convert_lead, name="lead_convert"),
    path("deals/", views.deal_list, name="deal_list"),
    path("deals/add/", views.deal_form, name="deal_add"),
    path("deals/<int:pk>/edit/", views.deal_form, name="deal_edit"),
    path("activities/", views.activity_list, name="activity_list"),
    path("activities/add/", views.activity_form, name="activity_add"),
    path("export/<str:record_type>/", views.export_csv, name="export_csv"),
]

