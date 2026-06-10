from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.companies.models import Company
from apps.core.models import CRUDUrlMixin, TimestampedModel


class Subcontractor(CRUDUrlMixin, TimestampedModel):
    """The subcontractor role attached to a company (its dossier).

    One company has at most one subcontractor dossier. Users are linked to it
    through ``SubcontractorProfile`` (one login today, a team later).
    """

    class WorkerCount(models.TextChoices):
        R1_5 = "1-5", _("1 à 5")
        R6_10 = "6-10", _("6 à 10")
        R11_25 = "11-25", _("11 à 25")
        R26_50 = "26-50", _("26 à 50")
        R51_100 = "51-100", _("51 à 100")
        R100_PLUS = "100+", _("Plus de 100")

    class CompanyAge(models.TextChoices):
        UNDER_3 = "under_3", _("Moins de 3 ans")
        BETWEEN_3_10 = "3_10", _("3 à 10 ans")
        OVER_10 = "over_10", _("Plus de 10 ans")

    company = models.OneToOneField(
        Company,
        on_delete=models.PROTECT,
        related_name="subcontractor",
        verbose_name=_("Entreprise"),
    )
    worker_count = models.CharField(
        _("Nombre d'employés"),
        max_length=10,
        choices=WorkerCount.choices,
        blank=True,
    )
    company_age = models.CharField(
        _("Ancienneté de l'entreprise"),
        max_length=10,
        choices=CompanyAge.choices,
        blank=True,
    )
    accepts_wir = models.BooleanField(_("Accepte le WIR"), default=False)
    introduction = models.TextField(_("Introduction"), blank=True)
    cover_photo = models.ImageField(
        _("Photo de couverture"),
        upload_to="subcontractors/covers/",
        blank=True,
        null=True,
    )
    profile_photo = models.ImageField(
        _("Photo de profil"),
        upload_to="subcontractors/profiles/",
        blank=True,
        null=True,
    )
    location = models.CharField(_("Localisation"), max_length=255, blank=True)
    branch = models.ManyToManyField(
        "tenders.Branch",
        blank=True,
        related_name="subcontractors",
        verbose_name=_("Branches"),
    )
    references = models.ManyToManyField(
        "Reference",
        blank=True,
        related_name="subcontractors",
        verbose_name=_("Références"),
    )

    class Meta:
        verbose_name = _("Sous-traitant")
        verbose_name_plural = _("Sous-traitants")

    def __str__(self):
        return str(self.company)


class SubcontractorProfile(TimestampedModel):
    """Links a user to a subcontractor dossier (the login).

    One subcontractor = one login today; the FK leaves the door open for teams later.
    """

    user = models.OneToOneField(
        "authentication.User",
        on_delete=models.CASCADE,
        related_name="subcontractor_profile",
        verbose_name=_("Utilisateur"),
    )
    subcontractor = models.ForeignKey(
        Subcontractor,
        on_delete=models.PROTECT,
        related_name="members",
        verbose_name=_("Sous-traitant"),
    )

    class Meta:
        verbose_name = _("Profil sous-traitant")
        verbose_name_plural = _("Profils sous-traitants")

    def __str__(self):
        return f"{self.user} — {self.subcontractor}"


class Reference(CRUDUrlMixin, TimestampedModel):
    """A reference/project showcase entry for a subcontractor."""

    title = models.CharField(_("Titre"), max_length=255)
    description = models.TextField(_("Description"), blank=True)
    start_date = models.DateField(_("Date de début"), blank=True, null=True)
    end_date = models.DateField(_("Date de fin"), blank=True, null=True)

    class Meta:
        verbose_name = _("Référence")
        verbose_name_plural = _("Références")

    def __str__(self):
        return self.title


class ReferenceImage(TimestampedModel):
    """An image attached to a reference."""

    reference = models.ForeignKey(
        Reference,
        on_delete=models.CASCADE,
        related_name="images",
        verbose_name=_("Référence"),
    )
    image = models.ImageField(_("Image"), upload_to="references/images/")
    description = models.TextField(_("Description"), blank=True)

    class Meta:
        verbose_name = _("Image de référence")
        verbose_name_plural = _("Images de référence")

    def __str__(self):
        return f"{self.reference} — {self.pk}"
