from django.db import transaction
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import status, generics
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response

from apps.depo.models.outgoing import Outgoing, OutgoingMaterial
from apps.depo.models.stock import Stock
from apps.api.serializers.depo import OutgoingMaterialSerializer, OutgoingSerializer, OutgoingListOnlySerializer
from apps.info.models import Warehouse
from apps.shared.utils import CustomPagination
from apps.shared.views import BaseListApiView


# ---------------------------------------------------------------------------------------
class OutgoingCreateView(generics.CreateAPIView):
    queryset = Outgoing.objects.all()
    serializer_class = OutgoingSerializer

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        outgoing_data = request.data.copy()
        outgoing_material_data = outgoing_data.pop('outgoing_materials', [])

        warehouse_id = outgoing_data.get('warehouse')
        warehouse = get_object_or_404(Warehouse, id=warehouse_id)

        if not request.user.is_authenticated or not warehouse.managers.filter(id=request.user.id).exists():
            raise PermissionDenied("У вас нет разрешения на выполнение операции прихода в этом складе.")

        outgoing_data['created_by'] = request.user.id if request.user.is_authenticated else None
        outgoing_data['data'] = timezone.now().date()

        outgoing_serializer = self.get_serializer(data=outgoing_data)
        outgoing_serializer.is_valid(raise_exception=True)

        outgoing = outgoing_serializer.save()

        outgoing_material_data = [{'outgoing': outgoing.id, **item} for item in outgoing_material_data]
        outgoing_material_serializer = OutgoingMaterialSerializer(data=outgoing_material_data, many=True)

        if outgoing_material_serializer.is_valid():
            outgoing_material_serializer.save()

            stocks_to_update = []
            for item in outgoing_material_data:
                material = item['material']
                amount = item['amount']
                warehouse = outgoing.warehouse

                stock, created = Stock.objects.get_or_create(material=material, warehouse=warehouse)
                stock.amount -= amount  # Adjusted for Outgoing
                stocks_to_update.append(stock)

            Stock.objects.bulk_update(stocks_to_update, ['amount'])

            headers = self.get_success_headers(outgoing_serializer.data)
            return Response(outgoing_serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        else:
            return Response(outgoing_material_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ---------------------------------------------------------------------------------------
class OutgoingListApiView(BaseListApiView):
    queryset = Outgoing.objects.all()
    serializer_class = OutgoingListOnlySerializer
    filterset_fields = ['warehouse', 'outgoing_type', 'status']
    search_fields = ['code']
    pagination_class = CustomPagination


# ---------------------------------------------------------------------------------------

class OutgoingMaterialListView(generics.ListAPIView):
    queryset = OutgoingMaterial.objects.all()
    serializer_class = OutgoingMaterialSerializer


# ---------------------------------------------------------------------------------------

class OutgoingDetailView(generics.RetrieveAPIView):
    queryset = Outgoing.objects.all()
    serializer_class = OutgoingSerializer

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)

        data = serializer.data

        outgoing_materials = OutgoingMaterial.objects.filter(outgoing=instance)
        outgoing_material_serializer = OutgoingMaterialSerializer(outgoing_materials, many=True)

        data['outgoing_materials'] = outgoing_material_serializer.data

        return Response(data)

# ---------------------------------------------------------------------------------------
