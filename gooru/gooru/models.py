from django.db import models
from django.conf import settings
from .managers import SoftDeleteManager, SoftDeleteManagerDeleted, SoftDeleteUserManager, SoftDeleteUserManagerDeleted
from django.utils.translation import gettext_lazy as _
#from .validators import *
from django.utils import timezone
from django.contrib.auth.models import AbstractUser
from rest_framework.authtoken.models import Token


class SoftDeleteUserAbstract(AbstractUser):
    class Meta:
        abstract = True

    deleted_on = models.DateTimeField(null=True, blank=True)

    objects = SoftDeleteUserManager()  # Expose non-deleted objects only
    objects_unfiltered = models.Manager()  # Expose ALL objects (used primarily in Admin panel)
    objects_deleted = SoftDeleteUserManagerDeleted()  # Expose all DELETED objects (used primarily in for testing)

    def delete(self):
        self.deleted_on = timezone.now()
        self.is_active = False
        self.save()

    def hard_delete(self):
        super(SoftDeleteUserAbstract, self).delete()


class SoftDeleteAbstract(models.Model):
    class Meta:
        abstract = True

    deleted_on = models.DateTimeField(null=True, blank=True)

    objects = SoftDeleteManager()  # Expose non-deleted objects only
    objects_unfiltered = models.Manager()  # Expose ALL objects (used primarily in Admin panel)
    objects_deleted = SoftDeleteManagerDeleted()  # Expose all DELETED objects (used primarily in for testing)

    def delete(self):
        self.deleted_on = timezone.now()
        self.save()

    def hard_delete(self):
        super(SoftDeleteAbstract, self).delete()