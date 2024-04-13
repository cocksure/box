from django.db import models
from apps.shared.models import BaseModel
from apps.shared.validators import code_name_validate
from apps.users.models import CustomUser


class MaterialType(models.Model):
	name = models.CharField(max_length=100)

	def __str__(self):
		return self.name


class Material(BaseModel):
	code = models.CharField(max_length=100, unique=True)
	name = models.CharField(max_length=100, unique=True)
	material_type = models.ForeignKey(MaterialType, on_delete=models.CASCADE, max_length=100)
	material_thickness = models.FloatField()

	def __str__(self):
		return self.name


class Warehouse(BaseModel):
	code = models.CharField(max_length=10, unique=True, null=True, blank=True)
	name = models.CharField(max_length=100, unique=True)
	location = models.CharField(max_length=150, null=True, blank=True)
	can_import = models.BooleanField(default=True, null=True, blank=True)
	can_export = models.BooleanField(default=False, null=True, blank=True)
	use_negative = models.BooleanField(default=False, null=True, blank=True)
	is_active = models.BooleanField(default=True, null=True, blank=True)
	managers = models.ManyToManyField(CustomUser, blank=True)

	def save(self, *args, **kwargs):
		code_name_validate(self)
		super().save(*args, **kwargs)

	def __str__(self):
		return self.name


class Firm(BaseModel):
	code = models.CharField(max_length=10, unique=True, null=True, blank=True)
	name = models.CharField(max_length=150)
	legal_address = models.CharField(max_length=150, null=True, blank=True)
	actual_address = models.CharField(max_length=150, null=True, blank=True)
	phone_number = models.CharField(max_length=13, null=True, blank=True)
	license_number = models.CharField(max_length=100, null=True, blank=True)

	def save(self, *args, **kwargs):
		code_name_validate(self)
		super().save(*args, **kwargs)

	def __str__(self):
		return self.name


class Specification(BaseModel):
	year = models.CharField(max_length=4)
	name = models.CharField(max_length=100)
	firm = models.ForeignKey(Firm, on_delete=models.SET_NULL, null=True, blank=True, default=None)

	def __str__(self):
		return self.name


class BoxSize(models.Model):
	name = models.CharField(max_length=100)

	def __str__(self):
		return self.name


class BoxType(models.Model):
	name = models.CharField(max_length=100)

	def __str__(self):
		return self.name
