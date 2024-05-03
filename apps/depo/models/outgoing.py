from django.core.exceptions import ValidationError

from apps.depo.services import validate_outgoing, validate_use_negative, validate_movement_outgoing
from apps.info.models import Material, Warehouse
from apps.shared.models import BaseModel
from django.db import models


# -------------------------------------------------------------------------------------
class Outgoing(BaseModel):
	class OutgoingType(models.TextChoices):
		OUTGO = 'расход', 'Расход'
		SALE = 'продажа', 'Продажа'
		MOVEMENT = 'перемешения', 'Перемещение'

	class OutgoingStatus(models.TextChoices):
		ACCEPT = 'Принят', 'Принят'
		REJECT = 'Отклонен', 'Отклонен'
		IN_PROGRESS = 'В ожидании', 'В ожидании'

	code = models.CharField(max_length=10, unique=True, editable=False, verbose_name="Код")
	data = models.DateField(editable=True, verbose_name="Дата")
	outgoing_type = models.CharField(max_length=20, choices=OutgoingType.choices, default=OutgoingType.MOVEMENT,
									 verbose_name="Тип исхода")
	warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, related_name='outgoing_warehouse',
								  verbose_name="Склад")
	to_warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, null=True, blank=True,
									 related_name='outgoing_to_warehouse', verbose_name="К складу")
	status = models.CharField(max_length=20, choices=OutgoingStatus.choices, default=OutgoingStatus.IN_PROGRESS,
							  null=True, blank=True, verbose_name="Статус")
	note = models.CharField(max_length=250, null=True, blank=True, verbose_name="Примечание")

	class Meta:
		verbose_name = "Расход"
		verbose_name_plural = "Расходы"
		indexes = [
			models.Index(fields=['code', ])
		]

	def save(self, *args, **kwargs):
		if not self.code:
			last_outgoing = Outgoing.objects.order_by('-id').first()
			if last_outgoing:
				last_id = last_outgoing.id
				new_id = int(last_id) + 1
				self.code = f'WA{str(new_id).zfill(6)}'
			else:
				self.code = 'WA000001'

		if self.outgoing_type in [self.OutgoingType.OUTGO, self.OutgoingType.SALE]:
			self.status = self.OutgoingStatus.ACCEPT
		super().save(*args, **kwargs)

	def clean(self):
		validate_outgoing(self)
		validate_movement_outgoing(self)
		if self.outgoing_type == self.OutgoingType.MOVEMENT and not self.to_warehouse:
			raise ValidationError({'to_warehouse': 'Выберите склад в поле "to_warehouse", так как тип - перемещения.'})
		if self.to_warehouse == self.warehouse:
			raise ValidationError({'to_warehouse': 'Нельзя перемещать товары на тот же самый склад.'})

		super().clean()

	def __str__(self):
		return self.code


# -------------------------------------------------------------------------------------


class OutgoingMaterial(models.Model):
	outgoing = models.ForeignKey(Outgoing, on_delete=models.CASCADE, related_name='outgoing_materials',
								 verbose_name="Исходящая поставка")
	material = models.ForeignKey(Material, on_delete=models.CASCADE, verbose_name="Материал")
	amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Количество")
	material_party = models.CharField(max_length=100, null=True, blank=True, verbose_name="Партия материала")
	comment = models.TextField(max_length=1000, null=True, blank=True, verbose_name="Комментарий")

	class Meta:
		verbose_name = "Материал расхода"
		verbose_name_plural = "Материалы расхода"

		def __str__(self):
			return f"{self.material} {self.amount}"
