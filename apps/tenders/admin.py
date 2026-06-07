from django.contrib import admin


from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import Branch, ExecutionType, Tender, TenderAttachment


class BranchAdmin(admin.ModelAdmin):
    list_display = ("name", "is_active", "is_root")
    list_filter = ("is_active",)
    search_fields = ("name",)
    ordering = ("name",)

    def is_root(self, obj):
        return obj.parent_id is None

    is_root.boolean = True
    is_root.short_description = _("Racine")


class ExecutionTypeAdmin(admin.ModelAdmin):
    list_display = ("name", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name",)
    ordering = ("name",)


class TenderAttachmentInline(admin.TabularInline):
    model = TenderAttachment
    extra = 1
    fields = ("file", "label")


class TenderAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "owner",
        "status",
        "procedure",
        "start_date",
        "application_deadline",
        "created_by",
    )
    list_filter = ("status", "procedure", "canton", "execution_type", "branch")
    search_fields = (
        "title",
        "description",
        "city",
        "zip_code",
        "material",
        "project_volume",
    )
    raw_id_fields = ("owner", "created_by")
    filter_horizontal = ("execution_type", "branch")
    inlines = (TenderAttachmentInline,)
    date_hierarchy = "start_date"
    ordering = ("-created_at",)


class TenderAttachmentAdmin(admin.ModelAdmin):
    list_display = ("tender", "label", "file")
    search_fields = ("label", "file", "tender__title")
    raw_id_fields = ("tender",)


admin.site.register(Branch, BranchAdmin)
admin.site.register(ExecutionType, ExecutionTypeAdmin)
admin.site.register(Tender, TenderAdmin)
admin.site.register(TenderAttachment, TenderAttachmentAdmin)