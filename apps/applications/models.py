from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.core.models import CRUDUrlMixin, TimestampedModel


class ApplicationStatus(models.TextChoices):
    PENDING = "pending", _("En attente")
    ACCEPTED = "accepted", _("Acceptée")
    REJECTED = "rejected", _("Rejetée")


class Application(CRUDUrlMixin, TimestampedModel):
    """A subcontractor's application (quote) to a client tender.

    One subcontractor can apply once per tender. The client then accepts or
    rejects the application; the status is visible to the subcontractor.
    """

    tender = models.ForeignKey(
        "tenders.Tender",
        on_delete=models.CASCADE,
        related_name="applications",
        verbose_name=_("Appel d'offres"),
    )
    subcontractor = models.ForeignKey(
        "subcontractors.Subcontractor",
        on_delete=models.CASCADE,
        related_name="applications",
        verbose_name=_("Sous-traitant"),
    )
    cover_letter = models.TextField(_("Message"), blank=True)
    quote_file = models.FileField(
        _("Offre / pièce jointe"),
        upload_to="application_quotes/",
        blank=True,
        null=True,
    )
    quote_amount = models.DecimalField(
        _("Montant de l'offre"),
        max_digits=12,
        decimal_places=2,
        blank=True,
        null=True,
    )
    status = models.CharField(
        _("Statut"),
        max_length=10,
        choices=ApplicationStatus.choices,
        default=ApplicationStatus.PENDING,
    )
    decided_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="decided_applications",
        verbose_name=_("Décidé par"),
    )
    decided_at = models.DateTimeField(_("Décidé le"), blank=True, null=True)

    class Meta:
        verbose_name = _("Candidature")
        verbose_name_plural = _("Candidatures")
        ordering = ("-created_at",)
        constraints = [
            models.UniqueConstraint(
                fields=("tender", "subcontractor"),
                name="unique_application_per_tender_subcontractor",
            )
        ]

    def __str__(self):
        return f"{self.subcontractor} — {self.tender}"


class FavoriteSubcontractor(TimestampedModel):
    """A subcontractor marked as a favourite by a client company."""

    company = models.ForeignKey(
        "companies.Company",
        on_delete=models.CASCADE,
        related_name="favorite_subcontractors",
        verbose_name=_("Entreprise"),
    )
    subcontractor = models.ForeignKey(
        "subcontractors.Subcontractor",
        on_delete=models.CASCADE,
        related_name="favorited_by",
        verbose_name=_("Sous-traitant"),
    )

    class Meta:
        verbose_name = _("Sous-traitant favori")
        verbose_name_plural = _("Sous-traitants favoris")
        ordering = ("-created_at",)
        constraints = [
            models.UniqueConstraint(
                fields=("company", "subcontractor"),
                name="unique_favorite_per_company_subcontractor",
            )
        ]

    def __str__(self):
        return f"{self.company} ♥ {self.subcontractor}"
