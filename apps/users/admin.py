from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.utils.translation import gettext_lazy as _

from apps.users.forms import UserCreationForm
from apps.users.models import Client, Subcontractor, User


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    add_form = UserCreationForm
    model = User
    ordering = ("-date_joined",)
    list_display = ("email", "first_name", "last_name", "role", "is_active", "is_staff")
    list_filter = ("role", "is_active", "is_staff", "language")
    search_fields = ("email", "first_name", "last_name")
    readonly_fields = ("date_joined", "last_login")
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (
            _("Informations personnelles"),
            {
                "fields": ("first_name", "last_name", "phone", "avatar", "language"),
            },
        ),
        (
            _("Rôle & permissions"),
            {
                "fields": (
                    "role",
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        (_("Dates"), {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "first_name",
                    "last_name",
                    "role",
                    "password1",
                    "password2",
                ),
            },
        ),
    )


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ("user", "company", "position", "is_company_admin")
    list_filter = ("is_company_admin",)
    search_fields = ("user__email", "company__name")
    autocomplete_fields = ("user", "company")


@admin.register(Subcontractor)
class SubcontractorAdmin(admin.ModelAdmin):
    list_display = ("user", "company")
    search_fields = ("user__email", "company__name")
    autocomplete_fields = ("user", "company")
