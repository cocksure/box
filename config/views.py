from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from apps.depo.models.incoming import Incoming
from django.db.models import Sum
from datetime import date

from apps.depo.models.outgoing import Outgoing


@login_required
def dashboard_view(request):
	# Получаем текущую дату
	today = date.today()

	# Расчет приходов за сегодня
	today_incomings = Incoming.objects.filter(data=today)
	today_incoming_sum = today_incomings.aggregate(total=Sum('incomingmaterial__amount'))['total'] or 0

	# Расчет приходов за все время
	all_incoming_sum = Incoming.objects.aggregate(total=Sum('incomingmaterial__amount'))['total'] or 0

	# Расчет продаж (расходов с типом "продажа") за сегодня
	today_sales = Outgoing.objects.filter(data=today, outgoing_type=Outgoing.OutgoingType.SALE)
	today_sales_sum = today_sales.aggregate(total=Sum('outgoing_materials__amount'))['total'] or 0

	# Расчет продаж (расходов с типом "продажа") за все время
	all_sales_sum = Outgoing.objects.filter(outgoing_type=Outgoing.OutgoingType.SALE)
	all_sales_sum = all_sales_sum.aggregate(total=Sum('outgoing_materials__amount'))['total'] or 0

	context = {
		'today_incoming_sum': today_incoming_sum,
		'all_incoming_sum': all_incoming_sum,
		'today_sales_sum': today_sales_sum,
		'all_sales_sum': all_sales_sum,
	}

	return render(request, 'dashboard.html', context)
