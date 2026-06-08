from django.contrib.auth.mixins import UserPassesTestMixin
from django.db.models import Exists, OuterRef, Q
from django.utils import timezone
from django_filters.views import FilterView
from django_tables2 import SingleTableMixin

from apps.documents.models import DocumentKind, DocumentStatus, ProofDocument
from apps.subscriptions.models import SubscriptionStatus

from .filters import SubcontractorFilter
from .models import Subcontractor
from .tables import SubcontractorTable

ACTIVE_SUBSCRIPTION_STATUSES = (
    SubscriptionStatus.ACTIVE,
    SubscriptionStatus.TRIALING,
)


class ClientAccessMixin(UserPassesTestMixin):
    """Restrict access to clients and staff/admin users."""

    def test_func(self):
        user = self.request.user
        return bool(
            user.is_authenticated and (user.is_staff or hasattr(user, "client_profile"))
        )


class SubcontractorListView(ClientAccessMixin, SingleTableMixin, FilterView):
    """Client-facing list of subcontractors with a filter sidebar."""

    model = Subcontractor
    table_class = SubcontractorTable
    filterset_class = SubcontractorFilter
    template_name = "subcontractors/subcontractor_list.html"

    def get_queryset(self):
        valid_insurance = ProofDocument.objects.filter(
            subcontractor=OuterRef("pk"),
            kind=DocumentKind.INSURANCE,
            status=DocumentStatus.VALID,
        ).filter(
            Q(valid_until__isnull=True) | Q(valid_until__gte=timezone.now().date())
        )
        return (
            Subcontractor.objects.filter(
                subscription__status__in=ACTIVE_SUBSCRIPTION_STATUSES
            )
            .select_related("company", "subscription")
            .prefetch_related("branch")
            .annotate(has_valid_insurance=Exists(valid_insurance))
        )

    def get_template_names(self):
        if self.request.htmx:
            return ["subcontractors/_subcontractor_table.html"]
        return [self.template_name]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["total_count"] = context["filter"].qs.count()
        return context
