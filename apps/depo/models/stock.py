from django.db import models
from apps.info.models import Material, Warehouse
from apps.shared.models import BaseModel


class Stock(BaseModel):
	material = models.ForeignKey(Material, on_delete=models.SET_NULL, null=True, verbose_name="Материал")
	warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, verbose_name="Склад")
	amount = models.IntegerField(default=0, verbose_name="Количество")

	class Meta:
		verbose_name = "Остаток на складе"
		verbose_name_plural = "Остатки на складе"
		indexes = [
			models.Index(fields=['material'])
		]

		def __str__(self):
			return f"{self.material} в {self.warehouse} ({self.amount} шт.)"
