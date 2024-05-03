from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from apps.info import models
from apps.info.models import BoxSize, BoxType, Brand, MaterialGroup, MaterialSpecialGroup
from apps.info.resources import MaterialResource


@admin.register(models.MaterialType)
class MaterialTypeAdmin(admin.ModelAdmin):
	list_display = ('name',)
	search_fields = ('name',)
	list_per_page = 100
	fields = ('name',)


@admin.register(models.Material)
class MaterialAdmin(ImportExportModelAdmin, admin.ModelAdmin):
	list_display = ('name', 'code', 'material_type', 'material_thickness', 'unit_of_measurement')
	search_fields = ('code', 'name',)
	list_filter = ('material_type',)
	list_per_page = 100
	date_hierarchy = 'created_time'
	readonly_fields = ('created_time', 'updated_time')
	fields = ('code', 'name', 'material_group', 'special_group', 'brand', 'material_type', 'material_thickness',
			  'unit_of_measurement', 'photo')
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
	list_filter = ('type_firm', 'is_active')
	list_per_page = 100
	date_hierarchy = 'created_time'
	readonly_fields = ('created_time', 'updated_time', 'created_by', 'updated_by')
	fieldsets = (
		('Basic Information', {
			'fields': (
				'code', 'name', 'type_firm', 'is_active', 'legal_address', 'actual_address', 'phone_number',
				'license_number', 'mfo',
			)
		}),
		('Timestamps', {
			'fields': ('created_time', 'created_by', 'updated_time', 'updated_by'),
			'classes': ('collapse',),
		}),
	)


@admin.register(BoxSize)
class BoxSizeAdmin(admin.ModelAdmin):
	fields = ('width', 'height', 'length')
	list_display = ('name', 'width', 'height', 'length')
	list_per_page = 100


@admin.register(MaterialSpecialGroup)
class MaterialSpecialGroupAdmin(admin.ModelAdmin):
	list_display = ('name',)
	list_per_page = 100


@admin.register(MaterialGroup)
class MaterialGroupAdmin(admin.ModelAdmin):
	list_display = ('name',)
	list_per_page = 100


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
	list_display = ('name',)
	list_per_page = 100


@admin.register(BoxType)
class BoxTypeAdmin(admin.ModelAdmin):
	list_display = ('name',)
	list_per_page = 100
