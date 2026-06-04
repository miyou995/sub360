from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.companies.const import CompanyType, SwissCanton
from apps.core.models import CRUDUrlMixin, TimestampedModel


class Company(CRUDUrlMixin, TimestampedModel):
    """A company on the platform — either a client (contractor) or a subcontractor.

    Client companies can group several users (a team); subcontractor companies
    map to a single user (one company = one login).
    """

    name = models.CharField(_("Raison sociale"), max_length=255)
    company_type = models.CharField(
        _("Type d'entreprise"),
        max_length=20,
        choices=CompanyType.choices,
        default=CompanyType.CLIENT,
    )
    uid = models.CharField(
        _("Numéro IDE / UID"),
        max_length=20,
        blank=True,
        help_text=_("Identifiant des entreprises suisse (ex: CHE-123.456.789)."),
    )
    email = models.EmailField(_("Email"), blank=True)
    phone = models.CharField(_("Téléphone"), max_length=30, blank=True)
    website = models.URLField(_("Site web"), blank=True)
    address = models.CharField(_("Adresse"), max_length=255, blank=True)
    zip_code = models.CharField(_("NPA"), max_length=10, blank=True)
    city = models.CharField(_("Localité"), max_length=120, blank=True)
    canton = models.CharField(
        _("Canton"),
        max_length=2,
        choices=SwissCanton.choices,
        blank=True,
    )

    class Meta:
        verbose_name = _("Entreprise")
        verbose_name_plural = _("Entreprises")
        ordering = ("name",)

    def __str__(self):
        return self.name
