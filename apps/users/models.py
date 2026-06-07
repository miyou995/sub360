from django.conf import settings
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.core.models import CRUDUrlMixin, TimestampedModel


def get_language_choices():
    return settings.LANGUAGES


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

