from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.core.models import CRUDUrlMixin, TimestampedModel
from apps.documents.const import DocumentKind, DocumentStatus
from apps.users.models import Subcontractor


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
