from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.core.models import CRUDUrlMixin, TimestampedModel
from apps.subcontractors.models import Subcontractor


class SubscriptionPackage(models.TextChoices):
    # Tiers à confirmer (project.md, Appendix B).
    BASIC = "basic", _("Basique")
    PRO = "pro", _("Pro")
    PREMIUM = "premium", _("Premium")


class SubscriptionStatus(models.TextChoices):
    INCOMPLETE = "incomplete", _("Incomplet")
    TRIALING = "trialing", _("Période d'essai")
    ACTIVE = "active", _("Actif")
    PAST_DUE = "past_due", _("Impayé")
    CANCELED = "canceled", _("Annulé")


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
