from rest_framework import viewsets
from apps.info import models
from apps.shared.utils import CustomPagination
from apps.api.serializers.info import WarehouseSerializer, MaterialSerializer, MaterialTypeSerializer, \
	BoxSizeSerializer, \
	BoxTypeSerializer


class WarehouseViewSetView(viewsets.ModelViewSet):
	queryset = models.Warehouse.objects.all()
	serializer_class = WarehouseSerializer
	filterset_fields = ['name']
	search_fields = ['code', 'name']
	pagination_class = CustomPagination

	def perform_create(self, serializer):
		serializer.save(created_by=self.request.user)

	def perform_update(self, serializer):
		serializer.save(updated_by=self.request.user)


class MaterialViewSetView(viewsets.ModelViewSet):
	queryset = models.Material.objects.all()
	serializer_class = MaterialSerializer
	filterset_fields = ['material_type']
	search_fields = ['code', 'name']
	pagination_class = CustomPagination

	def perform_create(self, serializer):
		serializer.save(created_by=self.request.user)

	def perform_update(self, serializer):
		serializer.save(updated_by=self.request.user)


class MaterialTypeViewSetView(viewsets.ModelViewSet):
	queryset = models.MaterialType.objects.all()
	serializer_class = MaterialTypeSerializer
	search_fields = ['code', 'name']
	pagination_class = CustomPagination


class BoxSizeViewSet(viewsets.ModelViewSet):
	queryset = models.BoxSize.objects.all()
	serializer_class = BoxSizeSerializer


class BoxTypeViewSet(viewsets.ModelViewSet):
	queryset = models.BoxType.objects.all()
	serializer_class = BoxTypeSerializer
