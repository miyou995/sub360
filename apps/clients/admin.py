from django.contrib import admin

from apps.clients.models import ClientProfile


@admin.register(ClientProfile)
class ClientProfileAdmin(admin.ModelAdmin):
    list_display = ("user","user__email", "company", "position", "is_company_admin")
    list_filter = ("is_company_admin",)
    search_fields = ("user__email", "company__name")
    autocomplete_fields = ("user", "company")
