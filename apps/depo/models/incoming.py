from django.db import models

from apps.depo.models.outgoing import Outgoing
from apps.depo.models.stock import Stock
from apps.depo.services import validate_incoming, process_incoming
from apps.info.models import Material, Warehouse
from apps.shared.models import BaseModel
from django.db.models import F


class Incoming(BaseModel):
	MOVEMENT = 'Перемещение'
	INVOICE = 'По накладной'

	INCOMING_TYPE = [
		(MOVEMENT, 'Перемещение'),
		(INVOICE, 'По накладной'),
	]

	data = models.DateField(verbose_name="Дата")
	warehouse = models.ForeignKey(Warehouse, on_delete=models.PROTECT, related_name='incoming_warehouse', null=True,
								  verbose_name="Склад")
	from_warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, null=True, blank=True,
									   related_name='incoming_from_warehouse', verbose_name="От склада")
	invoice = models.CharField(max_length=150, null=True, blank=True, verbose_name="Накладная")
	contract_number = models.CharField(max_length=150, null=True, blank=True, verbose_name="Номер контракта")
	outgoing = models.ForeignKey(Outgoing, on_delete=models.PROTECT, null=True, blank=True, verbose_name="Исходящий")
	note = models.CharField(max_length=250, null=True, blank=True, verbose_name="Примечание")
	incoming_type = models.CharField(choices=INCOMING_TYPE, null=True, blank=True, max_length=150,
									 verbose_name="Тип поступления")

	class Meta:
		verbose_name = "Приход"
		verbose_name_plural = "Приходы"

		indexes = [
			models.Index(fields=['warehouse', 'from_warehouse'])
		]

	def save(self, *args, **kwargs):
		process_incoming(self)

		super().save(*args, **kwargs)

	def clean(self):
		validate_incoming(self)

		super().clean()

	def __str__(self):
		return f"{self.warehouse} {self.data}"


class IncomingMaterial(models.Model):
	incoming = models.ForeignKey(Incoming, on_delete=models.CASCADE, verbose_name="Поступление")
	material = models.ForeignKey(Material, on_delete=models.CASCADE, verbose_name="Материал")
	amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Количество")
	material_party = models.CharField(max_length=100, null=True, blank=True, verbose_name="Партия материала")
	comment = models.TextField(max_length=1000, null=True, blank=True, verbose_name="Комментарий")

	def delete(self, *args, **kwargs):
		material = self.material
		warehouse = self.incoming.warehouse if hasattr(self, 'incoming') else None
		super().delete(*args, **kwargs)
		if warehouse:
			Stock.objects.filter(material=material, warehouse=warehouse).update(amount=F('amount') - self.amount)

	class Meta:
		verbose_name = "Материал прихода"
		verbose_name_plural = "Материалы прихода"

	def __str__(self):
		return f"{self.material} - {self.amount}"
