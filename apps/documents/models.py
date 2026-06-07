from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.core.models import CRUDUrlMixin, TimestampedModel
from apps.subcontractors.models import Subcontractor


class DocumentKind(models.TextChoices):
    INSURANCE = "insurance", _("Assurance (obligatoire)")
    LICENSE = "license", _("Licence / autorisation")
    VAT = "vat", _("Attestation TVA")
    OTHER = "other", _("Autre")


class DocumentStatus(models.TextChoices):
    VALID = "valid", _("Valide")
    EXPIRED = "expired", _("Expiré")
    REVIEW = "review", _("À vérifier")


class ProofDocument(CRUDUrlMixin, TimestampedModel):
    """A proof document uploaded by a subcontractor (insurance, license, ...)."""

    subcontractor = models.ForeignKey(
        Subcontractor,
        on_delete=models.CASCADE,
        related_name="documents",
        verbose_name=_("Sous-traitant"),
    )
    kind = models.CharField(
        _("Type de document"),
        max_length=20,
        choices=DocumentKind.choices,
    )
    file = models.FileField(_("Fichier"), upload_to="proof_documents/")
    valid_until = models.DateField(_("Valide jusqu'au"), blank=True, null=True)
    status = models.CharField(
        _("Statut"),
        max_length=10,
        choices=DocumentStatus.choices,
        default=DocumentStatus.REVIEW,
    )

    class Meta:
        verbose_name = _("Document justificatif")
        verbose_name_plural = _("Documents justificatifs")
        ordering = ("-created_at",)

    def __str__(self):
        return f"{self.get_kind_display()} — {self.subcontractor}"
