from django.db import models

from src.base.managers import FlagsQuerySet


class FlagsModel(models.Model):
    is_deleted = models.BooleanField(verbose_name='Удален', default=False)

    objects = FlagsQuerySet.as_manager()

    class Meta:
        abstract = True

    def is_available(self):
        return not self.is_deleted
