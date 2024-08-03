from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache
from .models import (
	MaterialType,
	Material,
	Warehouse,
	Firm,
	Specification,
	BoxSize,
	BoxType,
	MaterialGroup,
	MaterialSpecialGroup,
	Brand,
)

CACHE_KEYS = [
	'materialtype_list_data',
	'material_list_data',
	'warehouse_list_data',
	'firm_list_data',
	'specification_list_data',
	'boxsize_list_data',
	'boxtype_list_data',
	'materialgroup_list_data',
	'materialspecialgroup_list_data',
	'brand_list_data',
]


# Utility function to clear cache
def clear_all_cache():
	for key in CACHE_KEYS:
		cache.delete(key)


# Receiver to clear cache after save
@receiver(post_save, sender=MaterialType)
@receiver(post_save, sender=Material)
@receiver(post_save, sender=Warehouse)
@receiver(post_save, sender=Firm)
@receiver(post_save, sender=Specification)
@receiver(post_save, sender=BoxSize)
@receiver(post_save, sender=BoxType)
@receiver(post_save, sender=MaterialGroup)
@receiver(post_save, sender=MaterialSpecialGroup)
@receiver(post_save, sender=Brand)
def clear_cache_on_save(sender, **kwargs):
	clear_all_cache()


# Receiver to clear cache after delete
@receiver(post_delete, sender=MaterialType)
@receiver(post_delete, sender=Material)
@receiver(post_delete, sender=Warehouse)
@receiver(post_delete, sender=Firm)
@receiver(post_delete, sender=Specification)
@receiver(post_delete, sender=BoxSize)
@receiver(post_delete, sender=BoxType)
@receiver(post_delete, sender=MaterialGroup)
@receiver(post_delete, sender=MaterialSpecialGroup)
@receiver(post_delete, sender=Brand)
def clear_cache_on_delete(sender, **kwargs):
	clear_all_cache()
