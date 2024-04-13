from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from apps.info import models
from apps.info.models import BoxSize, BoxType
from apps.info.resources import MaterialResource


@admin.register(models.MaterialType)
class MaterialTypeAdmin(admin.ModelAdmin):
	list_display = ('name',)
	search_fields = ('name',)
	list_per_page = 100
	fields = ('name',)


@admin.register(models.Material)
class MaterialAdmin(ImportExportModelAdmin, admin.ModelAdmin):
	list_display = ('name', 'code', 'material_type', 'material_thickness',)
	search_fields = ('code', 'name',)
	list_filter = ('material_type',)
	list_per_page = 100
	date_hierarchy = 'created_time'
	readonly_fields = ('created_time', 'updated_time')
	fields = ('code', 'name', 'material_type', 'material_thickness')
	list_per_page = 100

	resource_class = MaterialResource


@admin.register(models.Warehouse)
class WarehouseAdmin(admin.ModelAdmin):
	list_display = ('name', 'code', 'location', 'can_import', 'can_export', 'use_negative', 'is_active')
	search_fields = ('code', 'name', 'location')
	list_filter = ('can_import', 'can_export', 'use_negative', 'is_active')
	list_per_page = 100
	date_hierarchy = 'created_time'
	readonly_fields = ('created_time', 'updated_time')

	fieldsets = (
		('Basic Information', {
			'fields': ('code', 'name', 'location', 'can_import', 'can_export', 'use_negative', 'is_active', 'managers')
		}),

		('Timestamps', {
			'fields': ('created_time', 'created_by', 'updated_time', 'updated_by'),
			'classes': ('collapse',),
		}),
	)


@admin.register(models.Specification)
class SpecificationAdmin(admin.ModelAdmin):
	list_display = ('name', 'year', 'firm')
	search_fields = ('id', 'name', 'firm')
	list_per_page = 100
	date_hierarchy = 'created_time'
	readonly_fields = ('created_time', 'updated_time')
	fields = ('name', 'year', 'firm', 'created_by', 'updated_by',)


@admin.register(models.Firm)
class FirmAdmin(admin.ModelAdmin):
	list_display = ('name', 'phone_number', 'code', 'created_by', 'created_time')
	search_fields = ('code', 'name')
	list_filter = ()
	list_per_page = 100
	date_hierarchy = 'created_time'
	readonly_fields = (
		'created_time', 'updated_time', 'created_by', 'updated_by')
	fieldsets = (
		('Basic Information', {
			'fields': (
				'code', 'name', 'legal_address', 'actual_address', 'phone_number',
				'license_number',
			)
		}),
		('Timestamps', {
			'fields': ('created_time', 'created_by', 'updated_time', 'updated_by'),
			'classes': ('collapse',),
		}),
	)


@admin.register(BoxSize)
class BoxSizeAdmin(admin.ModelAdmin):
	list_display = ('name',)
	list_per_page = 100


@admin.register(BoxType)
class BoxTypeAdmin(admin.ModelAdmin):
	list_display = ('name',)
	list_per_page = 100
