from django.shortcuts import get_object_or_404
from rest_framework import generics

from apps.production.models import BoxModel, BoxOrder, ProductionOrder, Process, BoxOrderDetail
from apps.api.serializers.production import BoxModelSerializer, BoxOrderSerializer, ProcessSerializer, \
	ProductionOrderSerializer
from rest_framework.permissions import BasePermission
from rest_framework.response import Response
from datetime import datetime
from rest_framework import status


class BoxModelListCreate(generics.ListCreateAPIView):
	queryset = BoxModel.objects.all()
	serializer_class = BoxModelSerializer
	filterset_fields = ['box_type']
	search_fields = ['material__name', 'name']


class BoxModelDetail(generics.RetrieveUpdateDestroyAPIView):
	queryset = BoxModel.objects.all()
	serializer_class = BoxModelSerializer


class BoxOrderListCreate(generics.ListCreateAPIView):
	queryset = BoxOrder.objects.all()
	serializer_class = BoxOrderSerializer
	filterset_fields = ['status', ]
	search_fields = ['specification', 'id']

	def create(self, request, *args, **kwargs):
		request.data['created_by'] = request.user.id
		request.data['data'] = datetime.now().date()

		serializer = self.get_serializer(data=request.data)
		serializer.is_valid(raise_exception=True)
		self.perform_create(serializer)
		headers = self.get_success_headers(serializer.data)
		return Response(serializer.data, status=201, headers=headers)


class ProductionOrderCreate(generics.CreateAPIView):
	serializer_class = ProductionOrderSerializer

	def create(self, request, *args, **kwargs):
		box_order_detail_id = self.kwargs.get('pk')
		box_order_detail = get_object_or_404(BoxOrderDetail, pk=box_order_detail_id)

		production_order = ProductionOrder.objects.create(
			box_order_detail=box_order_detail,
			shipping_date=datetime.now().date(),
			amount=box_order_detail.amount
		)

		serializer = ProductionOrderSerializer(production_order)
		return Response(serializer.data, status=201)


class IsDirectorOrReadOnly(BasePermission):
	def has_permission(self, request, view):
		if request.method in ['POST', 'PUT', 'PATCH', 'DELETE']:
			return request.user.is_authenticated and request.user.is_director
		return True


class BoxOrderDetailView(generics.RetrieveUpdateDestroyAPIView):
	permission_classes = [IsDirectorOrReadOnly]
	queryset = BoxOrder.objects.all()
	serializer_class = BoxOrderSerializer

	def put(self, request, *args, **kwargs):
		instance = self.get_object()
		serializer = self.get_serializer(instance, data=request.data, partial=True)
		serializer.is_valid(raise_exception=True)
		if 'status' in request.data:
			if instance.status is None:
				self.perform_update(serializer)
				if request.data['status'] == BoxOrder.BoxOrderStatus.ACCEPT:
					instance.confirm()
				elif request.data['status'] == BoxOrder.BoxOrderStatus.REJECT:
					instance.reject()
				return Response(serializer.data)
			else:
				return Response({"detail": "Order has already been confirmed or rejected."},
								status=status.HTTP_400_BAD_REQUEST)
		return Response(serializer.data)


class ProcessListCreate(generics.ListCreateAPIView):
	queryset = Process.objects.all()
	serializer_class = ProcessSerializer
