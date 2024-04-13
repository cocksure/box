from django.db import transaction
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework.generics import ListAPIView
from rest_framework.views import APIView

from apps.depo.models.outgoing import OutgoingMaterial, Outgoing
from apps.depo.models.stock import Stock
from apps.shared.utils import CustomPagination
from apps.shared.views import BaseListApiView

from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.decorators import action
from apps.api.serializers.depo import StockSerializer, OutgoingMaterialSerializer, OutgoingSerializer, \
	IncomingMaterialSerializer, IncomingSerializer


# ----------------------------------------------------------------------------------------
class StockListApiView(BaseListApiView):
	queryset = Stock.objects.all()
	serializer_class = StockSerializer
	filterset_fields = ['material_type__name', 'warehouse']
	search_fields = ['material__name', ]
	pagination_class = CustomPagination

	@action(detail=True, methods=['get'])
	def transactions(self, request, pk=None):
		stock = self.get_object()
		self.check_object_permissions(self.request, stock)

		outgoing_transactions = OutgoingMaterial.objects.filter(
			material=stock.material,
			material_party=stock.material_party,
			status='В ожидании'
		)

		outgoing_serializer = OutgoingMaterialSerializer(outgoing_transactions, many=True)

		return Response({
			'outgoing_transactions': outgoing_serializer.data,
			'stock': StockSerializer(stock).data
		})


# ----------------------------------------------------------------------------------------
class StockDetailView(generics.RetrieveAPIView):
	queryset = Stock.objects.all()
	serializer_class = StockSerializer


# ----------------------------------------------------------------------------------------
class UnacceptedMaterialsListView(ListAPIView):
	serializer_class = OutgoingSerializer
	filterset_fields = ['warehouse']
	search_fields = [
		'outgoing_materials__material__name',
		'outgoing_materials__material_party__code'
	]
	pagination_class = CustomPagination

	def get_queryset(self):
		return Outgoing.objects.filter(status='В ожидании')

	def list(self, request, *args, **kwargs):
		queryset = self.filter_queryset(self.get_queryset())
		serializer = OutgoingSerializer(queryset, many=True)
		return Response(serializer.data)


# ----------------------------------------------------------------------------------------
class UnacceptedMaterialsDetailView(APIView):
	def get(self, request, outgoing_id, *args, **kwargs):
		outgoing = get_object_or_404(Outgoing, id=outgoing_id)

		if outgoing.status in [Outgoing.OutgoingStatus.ACCEPT, Outgoing.OutgoingStatus.REJECT]:
			return Response({"detail": "Товар уже обработан."}, status=status.HTTP_400_BAD_REQUEST)

		outgoing_serializer = OutgoingSerializer(outgoing)

		data = {
			'outgoing': outgoing_serializer.data,
			'outgoing_materials': outgoing_serializer.data['outgoing_materials'],
		}

		return Response(data)

	@transaction.atomic
	def post(self, request, outgoing_id, *args, **kwargs):
		outgoing = get_object_or_404(Outgoing, id=outgoing_id)

		action = request.data.get('action')

		if action == 'accept':
			if outgoing.status == Outgoing.OutgoingStatus.ACCEPT:
				return Response({"detail": "Товар уже отработан."}, status=status.HTTP_400_BAD_REQUEST)

			outgoing._skip_signal = True
			outgoing.status = Outgoing.OutgoingStatus.ACCEPT
			outgoing.updated_by = request.user if request.user.is_authenticated else None
			outgoing.save()
			outgoing._skip_signal = False

			outgoing.refresh_from_db()

			incoming_data = {
				'data': timezone.now().date(),
				'created_by': request.user.id if request.user.is_authenticated else None,
				'warehouse': outgoing.to_warehouse.pk,
				'from_warehouse': outgoing.warehouse.pk,
				'outgoing': outgoing_id
			}

			incoming_serializer = IncomingSerializer(data=incoming_data)
			if incoming_serializer.is_valid():
				incoming = incoming_serializer.save()

				incoming_material_data = []
				for outgoing_material in outgoing.outgoing_materials.all():
					incoming_material_data.append({
						'incoming': incoming.id,
						'material': outgoing_material.material_id,
						'amount': outgoing_material.amount,
						'color': outgoing_material.color,
						'material_party': outgoing_material.material_party_id,
					})

				incoming_material_serializer = IncomingMaterialSerializer(data=incoming_material_data, many=True)
				if incoming_material_serializer.is_valid():
					incoming_material_serializer.save()

					stocks_to_update = []
					for item in outgoing.outgoing_materials.all():
						material = item.material
						amount = item.amount
						warehouse = outgoing.to_warehouse

						stock, created = Stock.objects.get_or_create(material=material, warehouse=warehouse)
						stock.amount += amount
						stocks_to_update.append(stock)

					Stock.objects.bulk_update(stocks_to_update, ['amount'])

					return Response({"detail": "Товар успешно принят."}, status=status.HTTP_200_OK)
				else:
					return Response({"detail": "Ошибка при сохранении материалов во входящий товар."},
									status=status.HTTP_400_BAD_REQUEST)
			else:
				return Response({"detail": "Ошибка при создании входящего товара."}, status=status.HTTP_400_BAD_REQUEST)

		elif action == 'reject':

			if outgoing.status == Outgoing.OutgoingStatus.REJECT:
				return Response({"detail": "Товар уже отработан."}, status=status.HTTP_400_BAD_REQUEST)

			outgoing._skip_signal = True
			outgoing.status = Outgoing.OutgoingStatus.REJECT
			outgoing.updated_by = request.user if request.user.is_authenticated else None
			outgoing.save()
			outgoing._skip_signal = False

			for item in outgoing.outgoing_materials.all():
				material = item.material
				amount = item.amount
				from_warehouse = outgoing.warehouse

				from_stock, created = Stock.objects.get_or_create(material=material, warehouse=from_warehouse)
				from_stock.amount += amount
				from_stock.save()

			return Response({"detail": "Товар отклонен."}, status=status.HTTP_200_OK)
		else:
			return Response({"detail": "Неверное действие."}, status=status.HTTP_400_BAD_REQUEST)

# ----------------------------------------------------------------------------------------
