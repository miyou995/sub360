from django.conf import settings
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.companies.models import Company
from apps.core.models import CRUDUrlMixin, TimestampedModel
from apps.users.const import CompanyAge, WorkerCount


def get_language_choices():
    return settings.LANGUAGES


# class WorkerCount(models.TextChoices):
#     R1_5 = "1-5", _("1 à 5")
#     R6_10 = "6-10", _("6 à 10")
#     R11_25 = "11-25", _("11 à 25")
#     R26_50 = "26-50", _("26 à 50")
#     R51_100 = "51-100", _("51 à 100")
#     R100_PLUS = "100+", _("Plus de 100")


# class CompanyAge(models.TextChoices):
#     UNDER_3 = "under_3", _("Moins de 3 ans")
#     BETWEEN_3_10 = "3_10", _("3 à 10 ans")
#     OVER_10 = "over_10", _("Plus de 10 ans")


class UserManager(BaseUserManager):
    """Manager for the email-based custom user model."""

    use_in_migrations = True

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError(_("L'adresse email est obligatoire."))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self.db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError(_("Un superutilisateur doit avoir is_staff=True."))
        if extra_fields.get("is_superuser") is not True:
            raise ValueError(_("Un superutilisateur doit avoir is_superuser=True."))

        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin, CRUDUrlMixin, TimestampedModel):
    """Custom user identified by email (no username)."""

    email = models.EmailField(_("Adresse email"), unique=True)
    first_name = models.CharField(_("Prénom"), max_length=150, blank=True)
    last_name = models.CharField(_("Nom"), max_length=150, blank=True)
    phone = models.CharField(_("Téléphone"), max_length=30, blank=True)
    avatar = models.ImageField(
        _("Photo de profil"), upload_to="avatars/", blank=True, null=True
    )
    language = models.CharField(
        _("Langue"),
        max_length=2,
        choices=get_language_choices,
        default=settings.LANGUAGE_CODE,
    )

    is_active = models.BooleanField(_("Actif"), default=True)
    is_staff = models.BooleanField(_("Membre du staff"), default=False)
    date_joined = models.DateTimeField(_("Date d'inscription"), default=timezone.now)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = _("Utilisateur")
        verbose_name_plural = _("Utilisateurs")
        ordering = ("-date_joined",)

    def __str__(self):
        return self.get_full_name() or self.email

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    def get_short_name(self):
        return self.first_name or self.email

    @property
    def full_name(self):
        return self.get_full_name()

    def get_absolute_url(self):
        return reverse("users:profile")


class ClientProfile(TimestampedModel):
    """Links a user to a client company. Several profiles can share one company (team)."""

    user = models.OneToOneField(
        User,
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

    class Meta:
        verbose_name = _("Profil client")
        verbose_name_plural = _("Profils clients")

    def __str__(self):
        return f"{self.user} — {self.company}"


class Subcontractor(CRUDUrlMixin, TimestampedModel):
    """The subcontractor role attached to a company (its dossier).

    One company has at most one subcontractor dossier. Users are linked to it
    through ``SubcontractorProfile`` (one login today, a team later).
    """

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
    references = models.TextField(_("Références"), blank=True)

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
        User,
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
