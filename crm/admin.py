from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Activity, Company, Contact, Deal, Lead, User
from .forms import LeadForm


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (("CRM role", {"fields": ("role",)}),)
    add_fieldsets = UserAdmin.add_fieldsets + (("CRM role", {"fields": ("role",)}),)


def administrator_access(request):
    user = request.user
    return user.is_active and user.is_staff and user.role == User.ADMIN


admin.site.has_permission = administrator_access
@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    # Staff admin follows the same conversion rule as the normal CRM form.
    form = LeadForm


admin.site.register([Company, Contact, Deal, Activity])
