from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Activity, Company, Contact, Deal, Lead, User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (("CRM role", {"fields": ("role",)}),)
    add_fieldsets = UserAdmin.add_fieldsets + (("CRM role", {"fields": ("role",)}),)


admin.site.register([Company, Contact, Lead, Deal, Activity])
