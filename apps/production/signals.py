from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache

from apps.production.models import BoxModel


@receiver(post_save, sender=BoxModel)
@receiver(post_delete, sender=BoxModel)
def clear_production_order_cache(sender, **kwargs):
	cache_key = 'boxmodel_list_data'
	cache.delete(cache_key)



