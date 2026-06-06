# Constants for the documents app.

from django.db import models
from django.utils.translation import gettext_lazy as _


class DocumentKind(models.TextChoices):
    INSURANCE = "insurance", _("Assurance (obligatoire)")
    LICENSE = "license", _("Licence / autorisation")
    VAT = "vat", _("Attestation TVA")
    OTHER = "other", _("Autre")


class DocumentStatus(models.TextChoices):
    VALID = "valid", _("Valide")
    EXPIRED = "expired", _("Expiré")
    REVIEW = "review", _("À vérifier")
