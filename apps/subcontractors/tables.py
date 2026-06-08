import django_tables2 as tables
from django.utils.translation import gettext_lazy as _

from apps.core.columns import InsuranceBadgeColumn, ManyToManyBadgeColumn

from .models import Subcontractor


class SubcontractorTable(tables.Table):
    """List of subcontractors shown to clients."""

    company = tables.Column(
        accessor="company__name",
        verbose_name=_("Entreprise"),
        order_by=("company__name",),
        attrs={"td": {"class": "fw-bold text-gray-800"}},
    )
    location = tables.Column(verbose_name=_("Localisation"), default="—")
    branch = ManyToManyBadgeColumn(verbose_name=_("Branches"), orderable=False)
    worker_count = tables.Column(verbose_name=_("Nombre d'employés"))
    insurance = InsuranceBadgeColumn(accessor="pk")

    class Meta:
        model = Subcontractor
        fields = ("company", "location", "branch", "worker_count", "insurance")
        sequence = ("company", "location", "branch", "worker_count", "insurance")
        attrs = {
            "class": "table align-middle table-row-dashed fs-6 gy-5 mb-0",
            "thead": {
                "class": "text-start text-muted fw-bold fs-7 text-uppercase gs-0"
            },
        }
        empty_text = _("Aucun sous-traitant ne correspond à votre recherche.")

    def render_worker_count(self, record):
        return record.get_worker_count_display() or "—"
