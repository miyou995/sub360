import logging
from datetime import date, datetime

from apps.billing.models import Bill, BillTypeConfig
from apps.core.mixins import BaseManageHtmxFormView, DeleteMixinHTMX
from apps.core.models import Potential
from apps.finance.models import (
    BillPayment,
    LedgerEntry,
    MiscTransaction,
    StaffPayment,
)
from apps.finance.tables import LedgerEntryTable
from apps.recurrent.models import Recurrent
from django.conf import settings
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils import translation
from django.utils.translation import gettext_lazy as _
from django.views.generic import TemplateView
from django_filters.views import FilterView
from django_tables2 import SingleTableMixin

from .forms import (
    PotentialModelForm,
)
from .tables import (
    PotentialHTMxTable,
)

logger = logging.getLogger(__name__)


def set_language(request, language="fr"):
    lang_code = language
    translation.activate(lang_code)
    request.session[settings.LANGUAGE_SESSION_KEY] = lang_code
    request.user.language = lang_code
    request.user.save()

    response = HttpResponseRedirect(request.META.get("HTTP_REFERER"))
    response.set_cookie(settings.LANGUAGE_COOKIE_NAME, lang_code)
    return response


class IndexView(TemplateView):
    template_name = "tables/table_partial.html"
    paginate_by = 4

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["size_class"] = "modal-lg mw-850px"
        context["ledger_table"] = LedgerEntryTable(
            data=LedgerEntry.objects.filter(date=date.today())
        )
        return context

    def get_template_names(self):
        if self.request.htmx:
            return ["tables/table_partial.html"]
        else:
            return ["index.html"]


# ----------------------------------Configuration----------------------------------


class ConfigugrationView(
    TemplateView
):  # this is a generic view  thazt doens't have a mode lso we do a breadcrumb manually
    template_name = "configuration/configuration.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = _("Configuration")
        context["title"] = _("Configuration")
        context["parent_url"] = reverse("core:configuration")
        return context


class ManagePotentialHtmx(BaseManageHtmxFormView):
    permission_required = "core.add_potential"
    form_class = PotentialModelForm
    model = Potential
    hx_triggers = {
        "closeModal": "kt_modal",
        "refresh_table": None,
    }


class PotentialDeleteHTMX(DeleteMixinHTMX):
    permission_required = "core.delete_potential"
    model = Potential


class PotentialListView(PermissionRequiredMixin, SingleTableMixin, FilterView):
    permission_required = "core.view_potential"
    model = Potential

    template_name = "tables/table_partial.html"
    filterset_class = None  # Define your filterset class if needed
    table_class = PotentialHTMxTable  # Define your table class if needed

    def get_queryset(self):
        return Potential.objects.all()


class StatisticsView(
    PermissionRequiredMixin, TemplateView
):  # Needs to be adapted to the sub360 context, currently it is finance specific
    permission_required = "finance.can_view_statistique"
    template_name = "statistics.html"

    def _parse_dates(self):
        date_from = self.request.GET.get("date_from", "")
        date_to = self.request.GET.get("date_to", "")
        parsed_from = parsed_to = None
        try:
            if date_from:
                parsed_from = datetime.strptime(date_from, "%Y-%m-%d").date()
            if date_to:
                parsed_to = datetime.strptime(date_to, "%Y-%m-%d").date()
        except ValueError:
            pass
        return date_from, date_to, parsed_from, parsed_to

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        date_from, date_to, df, dt = self._parse_dates()
        context["date_from"] = date_from
        context["date_to"] = date_to

        # ── 1 & 2. Bill payments ──
        bp = BillPayment.objects.date_range(df, dt)
        client_bill_payments = bp.for_clients().total_amount()
        supplier_bill_payments = bp.for_suppliers().total_amount()

        # ── 3 & 4. Misc transactions ──
        mt = MiscTransaction.objects.date_range(df, dt)
        misc_income = mt.income().total_amount()
        misc_expense = mt.expense().total_amount()

        # ── 5. Staff payments ──
        staff_payments = StaffPayment.objects.date_range(df, dt).total_amount()

        # ── Totals ──
        total_income = client_bill_payments + misc_income
        total_expense = supplier_bill_payments + misc_expense + staff_payments
        context.update(
            {
                "total_income": total_income,
                "total_expence": total_expense,
                "net_balance": total_income - total_expense,
                "client_bill_payments": client_bill_payments,
                "misc_income": misc_income,
                "supplier_bill_payments": supplier_bill_payments,
                "misc_expense": misc_expense,
                "staff_payments": staff_payments,
            }
        )

        # ── 6 & 7. Unpaid bills remaining (Subquery avoids JOIN-fanout) ──
        context["client_bill_reste"] = (
            Bill.objects.for_clients()
            .with_payments_only()
            .unpaid()
            .date_range(df, dt, field="created_at")
            .total_remaining()
        )
        context["supplier_bill_reste"] = (
            Bill.objects.for_suppliers()
            .with_payments_only()
            .unpaid()
            .date_range(df, dt, field="created_at")
            .total_remaining()
        )

        # ── 8. Recurrent remaining ──
        context["recurrent_remaining_amount"] = (
            Recurrent.objects.with_financials().with_total_remaining_amount()
        )

        # ── 9. Per-account breakdown (single query) ──
        context["account_breakdown"] = LedgerEntry.objects.date_range(
            df, dt
        ).breakdown_by_account()

        # ── 10. Per bill-type breakdown ──
        bill_types = BillTypeConfig.objects.filter(
            is_active=True, has_payments=True
        ).order_by("ordering", "label")
        context["bill_type_breakdown"] = [
            {
                "label": bt.label,
                "slug": bt.slug,
                "is_supplier": bt.is_supplier,
                "total_paid": BillPayment.objects.date_range(df, dt)
                .for_bill_type(bt)
                .total_amount(),
                "total_unpaid": (
                    Bill.objects.for_bill_type(bt)
                    .unpaid()
                    .date_range(df, dt, field="created_at")
                    .total_remaining()
                ),
                "total_billed": (
                    Bill.objects.for_bill_type(bt)
                    .not_canceled()
                    .date_range(df, dt, field="created_at")
                    .total_billed()
                ),
            }
            for bt in bill_types
        ]

        return context
