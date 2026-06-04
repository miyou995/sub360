from django.contrib import admin

from apps.companies.models import Company


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ("name", "company_type", "uid", "city", "canton")
    list_filter = ("company_type", "canton")
    search_fields = ("name", "uid", "email", "city")
