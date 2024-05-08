from django.http import JsonResponse
from django.shortcuts import get_object_or_404

from apps.info.models import Warehouse
from django.contrib import messages


def check_material_availability(request):
	warehouse_id = request.POST.get('warehouse')

	warehouse = get_object_or_404(Warehouse, id=warehouse_id)

	if warehouse.has_enough_material(request.POST):
		return JsonResponse({'success': True})
	else:
		error_message = 'Недостаточно материалов на складе'
		messages.error(request, error_message)
		return JsonResponse({'error': 'Недостаточно материалов на складе'}, status=400)
