import uuid
import transliterate
from django.core.validators import FileExtensionValidator
from django.utils.text import slugify
from django.db import models

from apps.depo.models.stock import Stock
from apps.shared.models import BaseModel
from apps.users.models import CustomUser
from django.core.validators import MinValueValidator


class MaterialType(BaseModel):
	name = models.CharField(max_length=100, verbose_name="Название")

	def __str__(self):
		return self.name

	class Meta:
		verbose_name = "Тип материала"
		verbose_name_plural = "Типы материалов"


class Material(BaseModel):
	UNIT_CHOICES = (
		('sht', 'шт'),
		('sm', 'см'),
		('mm', 'мм'),
		('kg', 'кг'),
		('litr', 'л'),
	)

	code = models.CharField(max_length=100, unique=True, null=True, blank=True, verbose_name="Код")
	name = models.CharField(max_length=100, unique=True, verbose_name="Название")
	material_group = models.ForeignKey('MaterialGroup', on_delete=models.CASCADE, verbose_name="Группа материала")
	special_group = models.ForeignKey('MaterialSpecialGroup', on_delete=models.CASCADE,
									  verbose_name="Специальная группа")
	brand = models.ForeignKey('Brand', on_delete=models.SET_NULL, null=True, verbose_name="Бренд")
	material_type = models.ForeignKey(MaterialType, on_delete=models.CASCADE, max_length=100,
									  verbose_name="Тип материала")
	material_thickness = models.FloatField(verbose_name="Плотность(Г/м2)", null=True)
	unit_of_measurement = models.CharField(max_length=10, choices=UNIT_CHOICES, default=None,
										   verbose_name="Единица измерения")
	norm = models.DecimalField(
		max_digits=10,
		decimal_places=2,
		null=True,
		blank=True,
		verbose_name="Норма для 1 м2",
		validators=[MinValueValidator(0)]
	)
	photo = models.ImageField(
		upload_to='box_photos',
		default='box_photos/no-image.png',
		validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'heic'])],
		verbose_name="Изображение"
	)

	def __str__(self):
		return self.name

	class Meta:
		verbose_name = "Материал"
		verbose_name_plural = "Материалы"

	def save(self, *args, **kwargs):
		if not self.code:
			material_group_name = self.material_group.name[:5]
			transliterated_name = slugify(transliterate.translit(material_group_name, 'ru', reversed=True))
			short_uuid = str(uuid.uuid4())[:4]
			self.code = f"{transliterated_name}-{short_uuid}"
		super().save(*args, **kwargs)


class Warehouse(BaseModel):
	code = models.CharField(max_length=10, unique=True, null=True, blank=True, verbose_name="Код")
	name = models.CharField(max_length=100, unique=True, verbose_name="Название")
	location = models.CharField(max_length=150, null=True, blank=True, verbose_name="Местоположение")
	can_import = models.BooleanField(default=True, null=True, blank=True, verbose_name="Может импортировать")
	can_export = models.BooleanField(default=False, null=True, blank=True, verbose_name="Может экспортировать")
	use_negative = models.BooleanField(default=False, null=True, blank=True,
									   verbose_name="Использовать отрицательные значения")
	is_active = models.BooleanField(default=True, null=True, blank=True, verbose_name="Активен")
	managers = models.ManyToManyField(CustomUser, blank=True, verbose_name="Менеджеры")

	# Другие поля модели

	def has_enough_material(self, form_data, insufficient_materials=None):
		if insufficient_materials is None:
			insufficient_materials = []

		for key, value in form_data.items():
			if key.startswith('outgoing_material_'):
				material_id = value
				amount = form_data.get('outgoing_amount_' + key.split('_')[-1], 0)
				try:
					stock = Stock.objects.get(warehouse=self, material_id=material_id)
					if stock.amount < int(amount):
						insufficient_materials.append(
							{'material': stock.material.name, 'available_amount': stock.amount})
						return False
				except Stock.DoesNotExist:
					insufficient_materials.append(
						{'material': Material.objects.get(id=material_id).name, 'available_amount': 0})
					return False
		return True, insufficient_materials

	def __str__(self):
		return self.name

	class Meta:
		verbose_name = "Склад"
		verbose_name_plural = "Склады"


class Firm(BaseModel):
	SUPPLIER = 'supplier'
	CUSTOMER = 'customer'
	BOTH = 'both'

	FIRM_TYPES = [
		(SUPPLIER, 'Поставщик'),
		(CUSTOMER, 'Заказчик'),
		(BOTH, 'Поставщик и Заказчик'),
	]

	code = models.CharField(max_length=10, unique=True, null=True, blank=True, verbose_name="Код")
	name = models.CharField(max_length=150, verbose_name="Название")
	type_firm = models.CharField(max_length=20, choices=FIRM_TYPES, verbose_name="Тип фирмы")
	is_active = models.BooleanField(default=True, null=True, blank=True, verbose_name="Активна")
	legal_address = models.CharField(max_length=150, null=True, blank=True, verbose_name="Юридический адрес")
	actual_address = models.CharField(max_length=150, null=True, blank=True, verbose_name="Фактический адрес")
	phone_number = models.CharField(max_length=13, null=True, blank=True, verbose_name="Номер телефона")
	license_number = models.CharField(max_length=100, null=True, blank=True, verbose_name="Номер лицензии")
	mfo = models.CharField(max_length=5, null=True, blank=True, verbose_name="МФО")

	def __str__(self):
		return self.name

	class Meta:
		verbose_name = "Фирма"
		verbose_name_plural = "Фирмы"


class Specification(BaseModel):
	year = models.CharField(max_length=4, verbose_name="Год")
	name = models.CharField(max_length=100, verbose_name="Название")
	firm = models.ForeignKey(Firm, on_delete=models.SET_NULL, null=True, blank=True, default=None, verbose_name="Фирма")

	def __str__(self):
		return self.name

	class Meta:
		verbose_name = "Спецификация"
		verbose_name_plural = "Спецификации"


class BoxSize(BaseModel):
	name = models.CharField(max_length=100, null=True, blank=True, verbose_name="Название")

	width = models.PositiveIntegerField(verbose_name="Ширина")
	height = models.PositiveIntegerField(verbose_name="Высота")
	length = models.PositiveIntegerField(verbose_name="Длина")

	def save(self, *args, **kwargs):
		self.name = f"{self.length}x{self.width}x{self.height} мм"
		super().save(*args, **kwargs)

	def calculate_material_area(self, layers):
		if layers == 3:
			area = ((self.length + self.width) * 2 + 59) * (self.width + self.height + 8) / 1000000
		else:  # for 5 layers
			area = ((self.length + self.width) * 2 + 69) * (self.width + self.height + 16) / 1000000
		return round(area, 3)

	def __str__(self):
		return f"{self.length}x{self.width}x{self.height} мм"

	class Meta:
		verbose_name = "Размер коробки"
		verbose_name_plural = "Размеры коробок"


class BoxType(BaseModel):
	name = models.CharField(max_length=100, verbose_name="Название")

	def __str__(self):
		return self.name

	class Meta:
		verbose_name = "Тип коробки"
		verbose_name_plural = "Типы коробок"


class MaterialGroup(BaseModel):
	name = models.CharField(max_length=100, verbose_name="Название")

	def __str__(self):
		return str(self.name)

	class Meta:
		verbose_name = "Группа материалов"
		verbose_name_plural = "Группы материалов"


class MaterialSpecialGroup(BaseModel):
	name = models.CharField(max_length=100, verbose_name="Название")

	def __str__(self):
		return str(self.name)

	class Meta:
		verbose_name = "Специальная группа материалов"
		verbose_name_plural = "Специальные группы материалов"


class Brand(BaseModel):
	name = models.CharField(max_length=100, verbose_name="Название")

	def __str__(self):
		return str(self.name)

	class Meta:
		verbose_name = "Бренд"
		verbose_name_plural = "Бренды"
