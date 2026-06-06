from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.core.models import CRUDUrlMixin, TimestampedModel
from apps.subscriptions.const import SubscriptionPackage, SubscriptionStatus
from apps.users.models import Subcontractor


class Subscription(CRUDUrlMixin, TimestampedModel):
    """A subcontractor's paid subscription. One dossier = one subscription."""

    subcontractor = models.OneToOneField(
        Subcontractor,
        on_delete=models.CASCADE,
        related_name="subscription",
        verbose_name=_("Sous-traitant"),
    )
    package = models.CharField(
        _("Forfait"),
        max_length=20,
        choices=SubscriptionPackage.choices,
    )
    status = models.CharField(
        _("Statut"),
        max_length=20,
        choices=SubscriptionStatus.choices,
        default=SubscriptionStatus.INCOMPLETE,
    )
    current_period_end = models.DateTimeField(
        _("Fin de la période en cours"), blank=True, null=True
    )

    class Meta:
        verbose_name = _("Abonnement")
        verbose_name_plural = _("Abonnements")

    def __str__(self):
        return f"{self.subcontractor} — {self.get_package_display()}"

    @property
    def is_active(self):
        return self.status in (
            SubscriptionStatus.ACTIVE,
            SubscriptionStatus.TRIALING,
        )
