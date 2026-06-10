from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.companies.models import Company
from apps.core.models import CRUDUrlMixin, TimestampedModel


class ClientProfile(TimestampedModel, CRUDUrlMixin):
    """Links a user to a client company. Several profiles can share one company (team)."""

    user = models.OneToOneField(
        "authentication.User",
        on_delete=models.CASCADE,
        related_name="client_profile",
        verbose_name=_("Utilisateur"),
    )
    company = models.ForeignKey(
        Company,
        on_delete=models.PROTECT,
        related_name="client_members",
        verbose_name=_("Entreprise"),
    )
    position = models.CharField(_("Fonction"), max_length=150, blank=True)
    is_company_admin = models.BooleanField(
        _("Administrateur de l'équipe"), default=False
    )

    # def get_absolute_url(self):
    #     # return reverse('users:detail_user', kwargs={'pk': self.pk})

    class Meta:
        verbose_name = _("Profil client")
        verbose_name_plural = _("Profils clients")

    def __str__(self):
        return f"{self.user} — {self.company}"
