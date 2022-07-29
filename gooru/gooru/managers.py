from django.db import models
from django.db.models import QuerySet
from django.utils import timezone
from django.contrib.auth.models import UserManager


class SoftDeleteQuerySet(QuerySet):
    """
    Prevents objects from being hard-deleted. Instead, sets the
    ``date_deleted``, effectively soft-deleting the object.
    """

    def delete(self):
        for obj in self:
            obj.deleted_on=timezone.now()
            obj.save()

    def hard_delete(self):
        super(SoftDeleteQuerySet, self).delete()


class SoftDeleteManager(models.Manager):
    """
    Only exposes objects that have NOT been soft-deleted.
    """

    def get_queryset(self):
        return SoftDeleteQuerySet(self.model, using=self._db).filter(
            deleted_on__isnull=True)


class SoftDeleteManagerDeleted(models.Manager):
    """
    Only exposes objects that have NOT been soft-deleted.
    """

    def get_queryset(self):
        return SoftDeleteQuerySet(self.model, using=self._db).filter(
            deleted_on__isnull=False)


class UserQuerySet(SoftDeleteQuerySet):

    def create(self, **kwargs):
        kwargs['username'] = kwargs.get('email')
        obj = self.model(**kwargs)
        self._for_write = True
        obj.save(force_insert=True, using=self.db)
        return obj

    def update(self, **kwargs) -> int:
        for obj in self:
            obj.username = obj.email
            obj.save()
        return super().update(**kwargs)


class SoftDeleteUserManager(UserManager):
    """
    Only exposes users that have NOT been soft-deleted.
    """

    def get_queryset(self):
        return UserQuerySet(self.model, using=self._db).filter(
            deleted_on__isnull=True)


class SoftDeleteUserManagerDeleted(models.Manager):
    """
    Only exposes objects that have NOT been soft-deleted.
    """

    def get_queryset(self):
        return UserQuerySet(self.model, using=self._db).filter(
            deleted_on__isnull=False)
