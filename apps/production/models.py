from decimal import Decimal

from django.core.validators import FileExtensionValidator, MinValueValidator
from django.db import models

from apps.depo.models.outgoing import OutgoingMaterial
from apps.info.models import Material, BoxSize, BoxType, Firm, Specification
from apps.shared.models import BaseModel
from apps.users.models import CustomUser


class Process(models.Model):
	name = models.CharField(max_length=100, unique=True, verbose_name="Название")
	queue = models.PositiveIntegerField(verbose_name="Очеред", blank=True, null=True, default=None)

	def __str__(self):
		return self.name

	class Meta:
		verbose_name = "Процесс"
		verbose_name_plural = "Процессы"


class TypeWork(models.Model):
	name = models.CharField(max_length=100, unique=True, verbose_name="Вид работы")
	process = models.ManyToManyField(Process, verbose_name="Процесс")

	def __str__(self):
		return self.name

	class Meta:
		verbose_name = "Вид работы"
		verbose_name_plural = "Виды работ"


class BoxModel(BaseModel):
	CLOSURE_TYPE_CHOICES = (
		(1, "Склейка"),
		(2, "Клапаны"),
		(3, "Автозамок"),
		(4, "Скобы"),
		(5, "Ленты или бандероли"),
		(6, "Крючки или зажимы"),
		(7, "Вкладыш"),
		(8, "Магниты"),
	)
	ADDITIONAL_PROPERTIES_CHOICES = (
		(1, "Влагостойкость"),
		(2, "Устойчивость к воздействию"),
		(3, "Экологичность"),
		(4, "Теплоизоляция"),
		(5, "Антистатические свойства"),
	)

	LAYER_CHOICES = (
		(3, '3 слоя'),
		(5, '5 слоев'),
	)

	name = models.CharField(max_length=100, unique=True, verbose_name="Название")
	material = models.ManyToManyField(Material, related_name='box_models', verbose_name="Материалы")
	additional_materials = models.ManyToManyField(Material, related_name='additional_box_models', blank=True,
												  verbose_name="Дополнительные материалы")

	photo = models.ImageField(
		upload_to='box_photos',
		default='box_photos/box_foto.png',
		validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'heic'])],
		verbose_name="Изображение"
	)
	box_size = models.ForeignKey(BoxSize, on_delete=models.SET_NULL,
								 blank=True, null=True, related_name='box_models_with_size',
								 verbose_name="Размер коробки")
	box_type = models.ForeignKey(BoxType, on_delete=models.SET_NULL,
								 blank=True, null=True, related_name='box_models_with_type',
								 verbose_name="Тип коробки")

	closure_type = models.IntegerField(choices=CLOSURE_TYPE_CHOICES, verbose_name="Тип замыкания", blank=True,
									   null=True)
	additional_properties = models.IntegerField(choices=ADDITIONAL_PROPERTIES_CHOICES, blank=True, null=True,
												verbose_name="Дополнительные свойства")
	max_load = models.CharField(max_length=50, blank=True, null=True, verbose_name="Максимальная нагрузка")
	color = models.CharField(max_length=50, blank=True, null=True, verbose_name="Цвет")
	comment = models.TextField(blank=True, null=True, verbose_name="Комментарий")
	grams_per_box = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True,
										verbose_name="Грамм на одну коробку")
	layers = models.IntegerField(choices=LAYER_CHOICES, default=3, verbose_name="Количество слоев")

	def calculate_total_material_area(self):
		if self.box_size:
			area = self.box_size.calculate_material_area(self.layers)
			return area
		return None

	def calculate_grams_per_box(self):
		area = self.calculate_total_material_area()
		if area:
			# Convert area to Decimal if it is not already
			area = Decimal(area)

			total_norm = Decimal(0)
			norms = [Decimal(material.norm) for material in self.material.all() if material.norm is not None]

			for norm in norms:
				total_norm += norm

			if total_norm:
				self.grams_per_box = area * total_norm
			else:
				self.grams_per_box = None
		else:
			self.grams_per_box = None

		print(f"Grams per box: {self.grams_per_box}")
		return self.grams_per_box

	def save(self, *args, **kwargs):
		print("Calculating grams per box...")

		if self.pk:  # Check if the instance is already saved
			# Calculate grams per box only if the instance is already saved
			self.calculate_grams_per_box()
			print(f"Grams per box before saving: {self.grams_per_box}")

		super().save(*args, **kwargs)

	class Meta:
		ordering = ['-created_time']
		verbose_name = "Модель коробки"
		verbose_name_plural = "Модели коробок"

	def __str__(self):
		return self.name


class BoxOrder(BaseModel):
	class BoxOrderStatus(models.TextChoices):
		ACCEPT = 'Одобрено', 'Одобрено'
		REJECT = 'Отклонено', 'Отклонено'
		NEW = 'НОВАЯ', 'НОВАЯ'

	class BoxTypeOrder(models.TextChoices):
		SAMPLE = 'Образец', 'Образец'
		EXPORT = 'Экспорт', 'Экспорт'
		INTERNAL_MARKET = 'Внутренный рынок', 'Внутренный рынок'
		SERVICE = 'Услуга', 'Услуга'

	data = models.DateField(editable=True, verbose_name="Дата")
	customer = models.ForeignKey(Firm, models.SET_NULL, verbose_name="Клиент", null=True)
	buyer = models.ForeignKey(Firm, models.SET_NULL, related_name='buyers', verbose_name="Покупатель", null=True)
	status = models.CharField(choices=BoxOrderStatus.choices, default=BoxOrderStatus.NEW, null=True, blank=True,
							  max_length=20, verbose_name="Статус")
	type_order = models.CharField(max_length=100, choices=BoxTypeOrder.choices, verbose_name="Тип заказа")
	specification = models.ForeignKey(Specification, on_delete=models.SET_NULL, null=True, verbose_name="Спецификация")
	manager = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Менеджер")
	date_of_production = models.DateField(editable=True, verbose_name="Дата производства")

	def new(self):
		if self.status is None:
			self.status = self.BoxOrderStatus.NEW
			self.save()

	def confirm(self):
		if self.status == self.BoxOrderStatus.NEW:
			self.status = self.BoxOrderStatus.ACCEPT
			self.save()

	def reject(self):
		if self.status == self.BoxOrderStatus.NEW:
			self.status = self.BoxOrderStatus.REJECT
			self.save()

	def __str__(self):
		return f"Заказ - {self.id}"

	class Meta:
		verbose_name = "Заказ коробки"
		verbose_name_plural = "Заказы коробок"


class BoxOrderDetail(models.Model):
	box_order = models.ForeignKey(BoxOrder, on_delete=models.CASCADE, verbose_name="Заказ коробки")
	box_model = models.ForeignKey(BoxModel, on_delete=models.CASCADE, verbose_name="Модель коробки")
	amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)],
								 verbose_name="Количество")

	def __str__(self):
		return f"{self.box_order} - {self.box_model}"

	class Meta:
		verbose_name = "Детали заказа коробки"
		verbose_name_plural = "Детали заказов коробок"


class ProductionOrder(BaseModel):
	class ProductionOrderStatus(models.TextChoices):
		IN_PROGRESS = 'В работе', 'В работе'
		COMPLETED = 'ЗАКОНЧЕНО', 'ЗАКОНЧЕНО'
		NOT_STARTED = 'НОВАЯ', 'НОВАЯ'
		PACKED = 'Упаковано', 'Упаковано'

	code = models.CharField(max_length=20, unique=True, blank=True, verbose_name="Код")
	box_order_detail = models.ForeignKey(BoxOrderDetail, on_delete=models.CASCADE, related_name='production_orders',
										 blank=True, null=True, verbose_name="Детали заказа коробки")
	shipping_date = models.DateField(verbose_name="Дата доставки", null=True, blank=True)
	amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Количество")
	packed_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Количество упаковано")
	status = models.CharField(max_length=20, choices=ProductionOrderStatus.choices,
							  default=ProductionOrderStatus.NOT_STARTED, verbose_name="Статус")
	type_of_work = models.ForeignKey(TypeWork, on_delete=models.SET_NULL, null=True, verbose_name="Тип Работы")
	outgoing_material = models.ForeignKey(
		OutgoingMaterial,
		on_delete=models.CASCADE,
		related_name='production_orders_related',
		verbose_name="Исходящая поставка",
		null=True,
		blank=True
	)

	def save(self, *args, **kwargs):
		if not self.code:
			last_order = ProductionOrder.objects.all().order_by('id').last()
			if last_order:
				last_id = last_order.id
				self.code = f'BOX{last_id + 1:010d}'
			else:
				self.code = 'BOX0000000001'

		super().save(*args, **kwargs)

	class Meta:
		verbose_name = "Производственный заказ"
		verbose_name_plural = "Производственные заказы"

	def __str__(self):
		return self.code


class ProcessLog(models.Model):
	production_order = models.ForeignKey(ProductionOrder, on_delete=models.CASCADE, related_name='process_logs',
										 verbose_name="Заказ на производство")
	process = models.ForeignKey(Process, on_delete=models.CASCADE, verbose_name="Процесс")
	timestamp = models.DateTimeField(auto_now_add=True, verbose_name="Временная метка")

	class Meta:
		verbose_name = "Процесс производства"
		verbose_name_plural = "Процессы производства"

	def __str__(self):
		return f"Процесс для заказа {self.production_order.code}: {self.process.name}"
