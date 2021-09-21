# Create your models here.
from uuid import uuid4

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

from . import managers


# Create your models here.
class AbstractTrack(models.Model):
    uuid = models.UUIDField(_("uuid field"), unique=True, default=uuid4, editable=False)
    created = models.DateTimeField(_("created at"), auto_now_add=True)
    modified = models.DateTimeField(_("modified at"), auto_now=True)

    class Meta:
        abstract = True


class User(AbstractUser, AbstractTrack):
    full_name = models.CharField(max_length=50)
    email = models.EmailField(
        _("email address"),
        unique=True,
    )
    avatar = models.ImageField(upload_to="avatars/", null=True, blank=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    manager = managers.UserManager()

    def save(self, *args, **kwargs):
        self.username = self.email
        super().save(*args, **kwargs)
