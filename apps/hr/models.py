from django.db import models
from apps.shared.models import BaseModel
from config import settings


class Employee(BaseModel):
	full_name = models.CharField(max_length=100)
	user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)