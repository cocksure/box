from django.contrib import admin
from .models import Process, BoxModel, BoxOrder, BoxOrderDetail, ProductionOrder


# @admin.register(UploadImage)
# class UploadImageAdmin(admin.ModelAdmin):
# 	list_display = ['id', 'photo_preview']
# 	search_fields = ['id']
# 	list_per_page = 100
#
# 	def photo_preview(self, obj):
# 		if obj.photo:
# 			return mark_safe(f'<img src="{obj.photo.url}" width="70" height="auto">')
# 		else:
# 			return 'No Image'
#
# 	photo_preview.short_description = 'Photo Preview'


@admin.register(Process)
class ProcessAdmin(admin.ModelAdmin):
	list_display = ('name',)


@admin.register(BoxModel)
class BoxModelAdmin(admin.ModelAdmin):
	list_display = ('name', 'material', 'box_size', 'box_type')


@admin.register(BoxOrder)
class BoxOrderAdmin(admin.ModelAdmin):
	list_display = (
		'data', 'customer', 'status', 'type_order', 'specification', 'manager', 'date_of_production',)
	list_filter = ('status',)
	search_fields = ('customer', 'specification',)


@admin.register(BoxOrderDetail)
class BoxOrderDetailAdmin(admin.ModelAdmin):
	list_display = ('box_order', 'get_box_models_display', 'amount',)

	def get_box_models_display(self, obj):
		return str(obj.box_model)

	get_box_models_display.short_description = 'Box Models'


@admin.register(ProductionOrder)
class ProductionOrderAdmin(admin.ModelAdmin):
	list_display = ['id', 'shipping_date', 'amount']

# def display_box_order_details(self, obj):
#         return ", ".join([str(box_order_detail) for box_order_detail in obj.box_order_detail.all()])
