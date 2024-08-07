from django.urls import path
from .views import (
	MaterialTypeListCreate,
	MaterialListCreate,
	WarehouseListCreate,
	FirmListCreate,
	SpecificationListCreate,
	BoxSizeListCreate,
	BoxTypeListCreate, MaterialEditView, MaterialGroupListCreate, MaterialSpecialGroupListCreate, BrandListCreate,
	FirmUpdateView, MaterialGroupUpdateView,
)

app_name = 'info'

urlpatterns = [
	path('material-types/', MaterialTypeListCreate.as_view(), name='material_type-list'),
	path('materials/', MaterialListCreate.as_view(), name='material-list'),
	path('warehouses/', WarehouseListCreate.as_view(), name='warehouse-list'),
	path('firms/', FirmListCreate.as_view(), name='firm-list'),
	path('specifications/', SpecificationListCreate.as_view(), name='specification-list'),
	path('box-sizes/', BoxSizeListCreate.as_view(), name='box_size-list'),
	path('box-types/', BoxTypeListCreate.as_view(), name='box_type-list'),
	path('material-groups/', MaterialGroupListCreate.as_view(), name='material-group-list'),
	path('material-special-groups/', MaterialSpecialGroupListCreate.as_view(), name='special-group-list'),
	path('brands/', BrandListCreate.as_view(), name='brand-list'),

	path('material/int:<pk>/', MaterialEditView.as_view(), name='material-edit'),
	path('firm/<int:pk>/edit/', FirmUpdateView.as_view(), name='firm-update'),
	path('material-group/<int:pk>/edit/', MaterialGroupUpdateView.as_view(), name='material-group-update'),

]
