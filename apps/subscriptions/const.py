# Constants for the subscriptions app.

from django.db import models
from django.utils.translation import gettext_lazy as _


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
