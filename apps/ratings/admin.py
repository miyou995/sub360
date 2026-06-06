from django.contrib import admin

from apps.ratings.models import Rating


@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ("subcontractor", "company", "score", "status", "created_at")
    list_filter = ("status", "score")
    search_fields = ("subcontractor__company__name", "company__name", "comment")
    raw_id_fields = ("subcontractor", "company", "tender", "created_by")
    readonly_fields = ("created_at", "updated_at")
