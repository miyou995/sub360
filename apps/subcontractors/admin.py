from django.contrib import admin

from apps.subcontractors.models import Subcontractor, SubcontractorProfile


@admin.register(Subcontractor)
class SubcontractorAdmin(admin.ModelAdmin):
    list_display = ("company", "worker_count", "company_age", "accepts_wir")
    list_filter = ("worker_count", "company_age", "accepts_wir")
    search_fields = ("company__name",)
    autocomplete_fields = ("company",)


@admin.register(SubcontractorProfile)
class SubcontractorProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "subcontractor")
    search_fields = ("user__email", "subcontractor__company__name")
    autocomplete_fields = ("user", "subcontractor")
