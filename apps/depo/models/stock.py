from django.db import models
from apps.info.models import Material, Warehouse


class Stock(models.Model):
	material = models.ForeignKey(Material, on_delete=models.CASCADE)
	warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE)
	amount = models.IntegerField(default=0)

	class Meta:
		indexes = [
			models.Index(fields=['material'])
		]

	def __str__(self):
		return f"{self.material} в {self.warehouse} ({self.amount} шт.)"
