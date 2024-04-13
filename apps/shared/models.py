from django.db import models
from django.utils import timezone

from apps.users.models import CustomUser


class BaseModel(models.Model):
    created_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True,
                                   related_name='%(class)s_created_by')
    updated_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL,
                                   related_name='%(class)s_updated_by', blank=True, null=True)
    created_time = models.DateTimeField(default=timezone.now)  # Dobavljaem created_time
    updated_time = models.DateTimeField(auto_now=True, editable=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.updated_by and hasattr(self, 'request') and getattr(self, 'request'):
            self.updated_by = self.request.user

        super().save(*args, **kwargs)

    class Meta:
        ordering = ['-created_time']
        abstract = True
