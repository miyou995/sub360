from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.core.models import CRUDUrlMixin, TimestampedModel
from apps.users.models import Subcontractor


class VerificationReview(CRUDUrlMixin, TimestampedModel):
    """A back-office review of a subcontractor dossier (approve / reject)."""

    class VerificationStatus(models.TextChoices):
        PENDING = "pending", _("En attente")
        APPROVED = "approved", _("Approuvé")
        REJECTED = "rejected", _("Rejeté")

    subcontractor = models.ForeignKey(
        Subcontractor,
        on_delete=models.CASCADE,
        related_name="reviews",
        verbose_name=_("Sous-traitant"),
    )
    status = models.CharField(
        _("Statut"),
        max_length=10,
        choices=VerificationStatus.choices,
        default=VerificationStatus.PENDING,
    )
    reason = models.TextField(_("Motif"), blank=True)
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="verification_reviews",
        verbose_name=_("Vérifié par"),
    )
    reviewed_at = models.DateTimeField(_("Vérifié le"), blank=True, null=True)

    class Meta:
        verbose_name = _("Vérification")
        verbose_name_plural = _("Vérifications")
        ordering = ("-created_at",)

    def __str__(self):
        return f"{self.subcontractor} — {self.get_status_display()}"
