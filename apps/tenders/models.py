from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _
from tree_queries.models import TreeNode

from apps.companies.models import SwissCanton
from apps.core.models import CRUDUrlMixin, TimestampedModel


class Branch(CRUDUrlMixin, TimestampedModel, TreeNode):
    """A trade / branch from the shared catalogue, organised as a tree.

    Root nodes represent the top-level clusters; leaf nodes are the
    individual trades. Used both by tenders (the trade they target) and
    by subcontractors (the trades they offer).
    """

    name = models.CharField(_("Nom"), max_length=150, unique=True)
    is_active = models.BooleanField(_("Actif"), default=True)

    class Meta:
        verbose_name = _("Branche")
        verbose_name_plural = _("Branches")
        ordering = ("name",)

    def __str__(self):
        return self.name

    @property
    def is_root(self) -> bool:
        return self.parent_id is None


class ExecutionType(CRUDUrlMixin, TimestampedModel):
    """A type of execution attached to a tender (new build, renovation, ...)."""

    name = models.CharField(_("Nom"), max_length=100, unique=True)
    is_active = models.BooleanField(_("Actif"), default=True)

    class Meta:
        verbose_name = _("Type d'exécution")
        verbose_name_plural = _("Types d'exécution")
        ordering = ("name",)

    def __str__(self):
        return self.name


class TenderStatus(models.TextChoices):
    DRAFT = "draft", _("Brouillon")
    PUBLISHED = "published", _("Publié")
    CLOSED = "closed", _("Clôturé")
    AWARDED = "awarded", _("Attribué")


class TenderProcedure(models.TextChoices):
    PUBLIC = "public", _("Public")
    BY_INVITATION = "by_invitation", _("Sur invitation")


class Tender(CRUDUrlMixin, TimestampedModel):
    """A job / project tendered by a client company.

    Subcontractors browse published tenders and apply through the
    ``applications`` app. Status is set manually by the project lead.
    """

    title = models.CharField(_("Titre"), max_length=255)
    
    owner = models.ForeignKey(
        "companies.Company",
        on_delete=models.PROTECT,
        related_name="tenders",
        verbose_name=_("Entreprise"),
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="created_tenders",
        verbose_name=_("Créé par"),
    )
    description = models.TextField(_("Description"), blank=True)
    execution_type = models.ManyToManyField(
        "tenders.ExecutionType",
        blank=True,
        related_name="tenders",
        verbose_name=_("Types d'exécution"),
    )
    branch = models.ManyToManyField(
        "tenders.Branch",
        blank=True,
        related_name="tenders",
        verbose_name=_("Branches"),
    )
    canton = models.CharField(
        _("Canton"),
        max_length=2,
        choices=SwissCanton.choices,
        blank=True,
    )
    city = models.CharField(_("Localité"), max_length=120, blank=True)
    zip_code = models.CharField(_("NPA"), max_length=10, blank=True)
    start_date = models.DateField(_("Date de début"), blank=True, null=True)
    application_deadline = models.DateField(
        _("Délai de candidature"), blank=True, null=True
    )
    material_offered = models.BooleanField(_("Matériel fourni"), default=False)
    material = models.CharField(_("Matériel"), max_length=255, blank=True)
    project_volume = models.CharField(_("Volume du projet"), max_length=255, blank=True)
    procedure = models.CharField(
        _("Procédure"),
        max_length=20,
        choices=TenderProcedure.choices,
        default=TenderProcedure.PUBLIC,
    )
    status = models.CharField(
        _("Statut"),
        max_length=20,
        choices=TenderStatus.choices,
        default=TenderStatus.DRAFT,
    )

    class Meta:
        verbose_name = _("Appel d'offres")
        verbose_name_plural = _("Appels d'offres")
        ordering = ("-created_at",)

    def __str__(self):
        return self.title


class TenderAttachment(TimestampedModel):
    """A file attached to a tender (plans, specifications, ...)."""

    tender = models.ForeignKey(
        Tender,
        on_delete=models.CASCADE,
        related_name="attachments",
        verbose_name=_("Appel d'offres"),
    )
    file = models.FileField(_("Fichier"), upload_to="tenders/")
    label = models.CharField(_("Libellé"), max_length=255, blank=True)

    class Meta:
        verbose_name = _("Pièce jointe")
        verbose_name_plural = _("Pièces jointes")
        ordering = ("-created_at",)

    def __str__(self):
        return self.label or f"{self.tender} — {self.file.name}"
