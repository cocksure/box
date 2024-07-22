from django.contrib import admin

from .forms import ProductionOrderForm, ProcessLogForm
from .models import Process, BoxModel, BoxOrder, BoxOrderDetail, ProductionOrder, TypeWork, ProcessLog
from ..depo.admin import OutgoingInline, OutgoingMaterialInline


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
	list_display = ('name', 'queue')


@admin.register(TypeWork)
class TypeWorkAdmin(admin.ModelAdmin):
	list_display = ('name', 'display_processes')
	search_fields = ('name',)

	def display_processes(self, obj):
		return ", ".join([process.name for process in obj.process.all()])

	display_processes.short_description = 'Процессы'


@admin.register(BoxModel)
class BoxModelAdmin(admin.ModelAdmin):
	list_display = (
		'name', 'material', 'get_additional_materials', 'box_size', 'box_type', 'photo', 'closure_type',
		'additional_properties',
		'color', 'grams_per_box', 'comment', 'created_by', 'updated_by', 'created_time'
	)
	search_fields = ('name',)
	list_filter = ('box_type',)

	fieldsets = (
		(None, {
			'fields': (
				'name', 'material', 'additional_materials', 'box_size', 'box_type', 'photo', 'closure_type',
				'additional_properties',
				'color', 'comment'
			)
		}),
		('Audit Information', {
			'fields': ('created_by', 'updated_by', 'created_time'),
			'classes': ('collapse',)  # Collapsed by default
		}),
	)

	readonly_fields = ('created_by', 'updated_by', 'created_time')

	def save_model(self, request, obj, form, change):
		if not obj.pk:  # New object
			obj.created_by = request.user
		else:  # Existing object
			obj.updated_by = request.user
		super().save_model(request, obj, form, change)

	def get_additional_materials(self, obj):
		return ", ".join([material.name for material in obj.additional_materials.all()])

	get_additional_materials.short_description = 'Дополнительные материалы'


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
	search_fields = ('code',)
	list_display = ['code', 'box_order_detail', 'shipping_date', 'amount']
	inlines = [OutgoingMaterialInline]


def display_box_order_details(self, obj):
	return ", ".join([str(box_order_detail) for box_order_detail in obj.box_order_detail.all()])


@admin.register(ProcessLog)
class ProcessLogAdmin(admin.ModelAdmin):
	list_display = ['production_order', 'process', 'timestamp']
	search_fields = ['production_order__code', 'process__name']
	list_filter = ['process', 'timestamp']
	ordering = ['-timestamp']
