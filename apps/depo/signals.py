from decimal import Decimal

from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models.signals import post_delete, pre_save, post_save
from django.dispatch import receiver
from django.db.models import F
from .models import outgoing
from .models.incoming import IncomingMaterial, Incoming
from .models.outgoing import OutgoingMaterial, Outgoing
from .models.stock import Stock
from ..info.models import Warehouse


@receiver(post_save, sender=IncomingMaterial)
def update_stock_on_incoming(sender, instance, created, **kwargs):
	if created:
		material = instance.material
		warehouse = instance.incoming.warehouse

		stock, _ = Stock.objects.get_or_create(material=material, warehouse=warehouse)
		stock.save()


@receiver(pre_save, sender=outgoing.Outgoing)
def set_outgoing_status(sender, instance, **kwargs):
	if not hasattr(instance, '_skip_signal'):  # Проверяем, был ли сигнал вызван программно
		if instance.pk is None or instance.status == 'В ожидании':  # Устанавливаем статус при создании или если статус уже "В ожидании"
			if instance.outgoing_type == 'перемешения':
				instance.status = 'В ожидании'
			else:
				instance.status = 'Принят'


# -----------------------------------INCOMING start--------------------------------------------------------------------

@receiver(post_delete, sender=IncomingMaterial)
def update_stock_after_IncomingMaterial_deletion(sender, instance, **kwargs):
	material = instance.material
	warehouse = instance.incoming.warehouse if hasattr(instance, 'incoming') else None
	if warehouse:
		Stock.objects.filter(material=material, warehouse=warehouse).update(amount=F('amount') - instance.amount)


# -----------------------------------INCOMING finish--------------------------------------------------------------------

# -----------------------------------OUTGOING start--------------------------------------------------------------------

@receiver(post_delete, sender=OutgoingMaterial)
def update_stock_after_OutgoingMaterial_deletion(sender, instance, **kwargs):
	material = instance.material
	warehouse = instance.outgoing.warehouse if hasattr(instance, 'outgoing') else None
	if warehouse:
		Stock.objects.filter(material=material, warehouse=warehouse).update(amount=F('amount') + instance.amount)


# -----------------------------------OUTGOING finish--------------------------------------------------------------------


@receiver(pre_save, sender=OutgoingMaterial)
def check_stock(sender, instance, **kwargs):
	if not instance.outgoing.warehouse.use_negative:
		stock = Stock.objects.filter(material=instance.material, warehouse=instance.outgoing.warehouse).first()
		if stock is None or stock.amount < Decimal(instance.amount):
			available_amount = Decimal('0') if stock is None else stock.amount

			error_message = f"Недостаточно материала на складе. Доступно: {available_amount} {instance.material.unit_of_measurement}"

			raise ValidationError(error_message)


@receiver(post_save, sender=Incoming)
@receiver(post_delete, sender=Incoming)
def clear_incoming_cache(sender, **kwargs):
	cache_key = 'incoming_list_data'
	cache.delete(cache_key)


@receiver(post_save, sender=Outgoing)
@receiver(post_delete, sender=Outgoing)
def clear_outgoing_cache(sender, **kwargs):
	cache_key = 'outgoing_list_data'
	cache.delete(cache_key)
