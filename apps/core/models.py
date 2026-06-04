from django.db import models
from django.urls import reverse

# Create your models here.


class TimestampedModel(models.Model):
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name="Date de création"
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class CRUDUrlMixin:
    @classmethod
    def get_create_url(cls):
        return reverse(f"{cls._meta.app_label}:create_{cls._meta.model_name}")

    @classmethod
    def get_list_url(cls):
        return reverse(f"{cls._meta.app_label}:list_{cls._meta.model_name}")

    def get_update_url(self):
        return reverse(
            f"{self._meta.app_label}:update_{self._meta.model_name}",
            kwargs={"pk": self.pk},
        )

    def get_delete_url(self):
        return reverse(
            f"{self._meta.app_label}:delete_{self._meta.model_name}",
            kwargs={"pk": self.pk},
        )
