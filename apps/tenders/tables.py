# Tables for the tenders app.

import django_tables2 as tables
from django.utils.translation import gettext_lazy as _

from apps.core.columns import (
    ActionColumn,
    CustomCheckBoxColumn,
    HTMXUpdateLinkColumn,
)

from .models import Tender


class TenderTable(tables.Table):
    selection = CustomCheckBoxColumn(accessor="pk", orderable=False)
    title = HTMXUpdateLinkColumn(verbose_name=_("Titre"))
    status = tables.TemplateColumn(
        """
            {% if record.status == 'draft' %}
                <span class="badge badge-light-secondary">{{ record.get_status_display }}</span>
            {% elif record.status == 'published' %}
                <span class="badge badge-light-success">{{ record.get_status_display }}</span>
            {% elif record.status == 'closed' %}
                <span class="badge badge-light-warning">{{ record.get_status_display }}</span>
            {% elif record.status == 'awarded' %}
                <span class="badge badge-light-primary">{{ record.get_status_display }}</span>
            {% endif %}
        """,
        verbose_name=_("Statut"),
    )
    actions = ActionColumn()

    class Meta:
        model = Tender
        fields = (
            "selection",
            "title",
            "owner",
            "canton",
            "city",
            "procedure",
            "status",
            "application_deadline",
            "actions",
        )
        attrs = {"class": "table table-row-dashed table-row-gray-300 align-middle gs-0 gy-4"}
        order_by = ("-created_at",)
