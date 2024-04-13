from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission, PermissionsMixin


class CustomUser(AbstractUser, PermissionsMixin):
    is_director = models.BooleanField(default=False)
    photo = models.ImageField(upload_to='employee_photos', default='default-profile__picture.jpg')
    groups = models.ManyToManyField(Group, related_name='custom_user_groups', blank=True, verbose_name='groups')
    user_permissions = models.ManyToManyField(Permission, related_name='custom_user_permissions', blank=True,
                                              verbose_name='user permissions')
    # def save(self, *args, **kwargs):
    #     if not self.employee or self.employee.is_fired:
    #         self.is_active = False
    #     super().save(*args, **kwargs)

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"

    def __str__(self):
        return self.get_full_name()
