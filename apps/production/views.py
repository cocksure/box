from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.utils import timezone
from django.views import View
from django.views.generic import CreateView, DetailView
from weasyprint import HTML

from apps.depo.models.outgoing import Outgoing, OutgoingMaterial
from apps.depo.models.stock import Stock
from apps.info.models import Warehouse
from apps.production.forms import BoxModelForm, BoxOrderForm, BoxOrderDetailFormSet, ProductionOrderForm, \
	ProcessLogForm, ProcessLogFilterForm
from apps.production.models import BoxModel, BoxOrder, BoxOrderDetail, ProductionOrder, ProcessLog, Process
from django.http import JsonResponse, HttpResponseRedirect, HttpResponse
from django.db import transaction

from apps.shared.utils import generate_qr_code
from apps.shared.views import BaseListCreateView, BaseListView


class BoxModelListCreate(BaseListCreateView):
	model = BoxModel
	form_class = BoxModelForm
	template_name = "production/box_model_list.html"
	redirect_url = "production:box-model-list"


class BoxModelEditView(View, LoginRequiredMixin):
	def get(self, request, pk):
		boxmodel = get_object_or_404(BoxModel, pk=pk)
		form = BoxModelForm(instance=boxmodel)
		context = {'form': form, 'boxmodel': boxmodel}
		return render(request, 'production/box_model_edit.html', context)

	def post(self, request, pk):
		boxmodel = get_object_or_404(BoxModel, pk=pk)
		form = BoxModelForm(request.POST, instance=boxmodel)
		if form.is_valid():
			form.save()
			messages.success(request, 'Changes saved successfully.')
			return redirect('production:box-model-list')
		else:
			messages.error(request, 'Please correct the errors below.')
		context = {'form': form, 'boxmodel': boxmodel}
		return render(request, 'production/box_model_edit.html', context)


class BoxOrderListView(BaseListView):
	def get(self, request):
		box_orders = BoxOrder.objects.all().order_by('-created_time')

		# Получаем параметры запроса для фильтрации
		status = request.GET.get('status', 'all')
		type_order = request.GET.get('type_order', 'all')

		# Фильтрация по статусу
		if status and status != "all":
			box_orders = box_orders.filter(status=status)

		# Фильтрация по типу заказа
		if type_order and type_order != "all":
			box_orders = box_orders.filter(type_order=type_order)

		# Применяем пагинацию и поиск
		page_obj = self.apply_pagination_and_search(box_orders, request)

		context = {
			'items': page_obj,
			'box_orders': page_obj,
			'selected_status': status,
			'selected_type_order': type_order,
		}
		return render(request, "production/box_order_list.html", context)


class BoxOrderCreate(CreateView):
	model = BoxOrder
	form_class = BoxOrderForm
	template_name = 'production/box_order_create.html'

	def form_valid(self, form):
		order = form.save(commit=False)
		order.manager = self.request.user
		order.data = timezone.now()

		try:
			with transaction.atomic():
				order.save()
				print("Order saved:", order.id)

				detail_counter = int(self.request.POST.get('detail_counter', 0))

				for detail_index in range(1, detail_counter + 1):
					box_model_id = self.request.POST.get('box_model_' + str(detail_index))
					amount = self.request.POST.get('amount_' + str(detail_index))
					if box_model_id and amount:
						box_model = BoxModel.objects.get(id=box_model_id)
						BoxOrderDetail.objects.create(
							box_model=box_model,
							amount=amount,
							box_order=order
						)
						print("Detail created:", box_model_id, amount)

		except Exception as e:

			return JsonResponse({'error': str(e)}, status=400)
		else:

			return HttpResponseRedirect(reverse_lazy('production:box-order-list'))

	def form_invalid(self, form):
		return JsonResponse({'success': False, 'errors': form.errors}, status=400)

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		if self.object:
			context['order_detail_formset'] = BoxOrderDetailFormSet(
				self.request.POST if self.request.method == 'POST' else None,
				instance=self.object
			)
		else:
			context['order_detail_formset'] = BoxOrderDetailFormSet()
		return context


class BoxOrderDetailView(DetailView):
	model = BoxOrder
	template_name = 'production/box_order_detail.html'
	context_object_name = 'box_order'
	form_class = ProductionOrderForm

	def get(self, request, *args, **kwargs):
		box_order = self.get_object()
		order_details = box_order.boxorderdetail_set.all()
		form = self.form_class()
		return render(request, self.template_name, {
			self.context_object_name: box_order,
			'order_details': order_details,
			'form': form
		})

	def post(self, request, *args, **kwargs):
		box_order = self.get_object()
		new_status = request.POST.get('status')
		if new_status is not None:
			if new_status in [choice[0] for choice in box_order.BoxOrderStatus.choices]:
				box_order.status = new_status
				box_order.save()
				return redirect('production:box-order-detail', pk=box_order.pk)
			else:
				return JsonResponse({'error': 'Invalid status parameter'}, status=400)
		else:
			detail_id = request.POST.get('box_order_detail_id')

			try:
				detail = box_order.boxorderdetail_set.get(pk=detail_id)
			except BoxOrderDetail.DoesNotExist:
				return JsonResponse({'error': 'Invalid box order detail ID'}, status=400)

			form = self.form_class(request.POST)
			if form.is_valid():
				with transaction.atomic():
					production_order = form.save(commit=False)
					production_order.box_order_detail = detail
					production_order.amount = detail.amount
					production_order.save()

					# Создаем запись о расходе
					warehouse_id = 4
					try:
						warehouse = Warehouse.objects.get(pk=warehouse_id)
					except Warehouse.DoesNotExist:
						return JsonResponse({'error': 'Invalid warehouse ID'}, status=400)

					outgoing = Outgoing.objects.create(
						data=production_order.shipping_date,
						outgoing_type=Outgoing.OutgoingType.OUTGO,
						warehouse=warehouse,
						created_by=request.user
					)

					OutgoingMaterial.objects.create(
						outgoing=outgoing,
						material=detail.box_model.material,  # Предполагается, что в box_model есть связь с материалом
						amount=detail.amount
					)

					# Обновляем запасы на складе
					stock, created = Stock.objects.get_or_create(material=detail.box_model.material,
																 warehouse=warehouse)
					stock.amount -= detail.amount
					stock.save()

				return redirect('production:box-order-detail', pk=box_order.pk)
			else:
				messages.error(request, 'Недостаточно материалов на складе.')

				return JsonResponse({'error': 'Form validation failed'}, status=400)


class ProductionOrderListView(BaseListView):
	def get(self, request):
		production_orders = ProductionOrder.objects.all().order_by('-created_time')

		# Получаем параметры запроса для фильтрации
		status = request.GET.get('status', 'all')

		# Фильтрация по статусу
		if status and status != "all":
			production_orders = production_orders.filter(status=status)

		page_obj = self.apply_pagination_and_search_by_code(production_orders, request)

		context = {
			'items': page_obj,
			'production_orders': page_obj,
			'selected_status': status,
		}
		return render(request, "production/production_order_list.html", context)


def process_log_view(request):
	if request.method == 'POST':
		form = ProcessLogForm(request.POST)
		if form.is_valid():
			code = form.cleaned_data['production_order_code']
			try:
				production_order = ProductionOrder.objects.get(code=code)

				# Получаем тип работы и процессы в порядке очереди
				type_of_work = production_order.type_of_work
				processes = type_of_work.process.order_by('queue')

				# Найдем следующий процесс
				completed_processes = ProcessLog.objects.filter(production_order=production_order).values_list(
					'process', flat=True)
				next_process = processes.exclude(id__in=completed_processes).first()

				if next_process:
					# Создаем запись в журнале процесса
					ProcessLog.objects.create(production_order=production_order, process=next_process)
					messages.success(request,
									 f'Процесс "{next_process.name}" отмечен как выполненный для заказа {code}.')

					# Обновляем статус ProductionOrder
					if next_process.queue == processes.first().queue:
						production_order.status = production_order.ProductionOrderStatus.IN_PROGRESS
					elif next_process.queue == processes.last().queue:
						production_order.status = production_order.ProductionOrderStatus.COMPLETED

					production_order.save()
				else:
					messages.info(request, 'Все процессы для этого заказа уже выполнены.')

				return redirect('production:process_log')
			except ProductionOrder.DoesNotExist:
				messages.error(request, 'Заказ с таким кодом не найден.')
	else:
		form = ProcessLogForm()

	return render(request, 'production/process_log.html', {'form': form})


class ProcessLogListView(BaseListView):
	model = ProcessLog
	form_class = ProcessLogFilterForm
	template_name = 'production/process_log_list.html'

	def get_queryset(self):
		form = self.form_class(self.request.GET or None)
		logs = ProcessLog.objects.select_related('production_order', 'process')

		if form.is_valid():
			process = form.cleaned_data.get('process')
			status = form.cleaned_data.get('status')
			start_date = form.cleaned_data.get('start_date')
			end_date = form.cleaned_data.get('end_date')

			if process:
				logs = logs.filter(process=process)
			if status and status != 'all':
				logs = logs.filter(production_order__status=status)
			if start_date:
				logs = logs.filter(timestamp__gte=start_date)
			if end_date:
				logs = logs.filter(timestamp__lte=end_date)

		self.form = form
		return logs

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		processes = Process.objects.all()
		logs = self.get_queryset()

		# Создаем словарь для хранения информации о процессах для каждого заказа
		order_process_status = {}
		for log in logs:
			order_process_status.setdefault(log.production_order.id, {})
			order_process_status[log.production_order.id][log.process.id] = True

		page_obj = self.apply_pagination_and_search_by_code(logs, self.request)

		context.update({
			'form': self.form,
			'processes': processes,
			'items': page_obj,
			'order_process_status': order_process_status,
		})
		return context

	def get(self, request, *args, **kwargs):
		context = self.get_context_data()
		return render(request, self.template_name, context)


def generate_box_order_pdf(request, order_id):
	order = get_object_or_404(BoxOrder, id=order_id)
	html_string = render_to_string('pdf/box_order_pdf.html', {'order': order})
	html = HTML(string=html_string)
	pdf = html.write_pdf()

	response = HttpResponse(pdf, content_type='application/pdf')
	response['Content-Disposition'] = f'attachment; filename="box_order_{order_id}.pdf"'
	return response


def generate_production_order_pdf(request, production_order_id):
	production_order = get_object_or_404(ProductionOrder, id=production_order_id)

	qr_code_data = generate_qr_code(production_order.code)

	html_string = render_to_string('pdf/production_order_pdf.html',
								   {'order': production_order, 'qr_code_data': qr_code_data})

	html = HTML(string=html_string)
	pdf = html.write_pdf()

	response = HttpResponse(pdf, content_type='application/pdf')
	response['Content-Disposition'] = f'attachment; filename="production_order_{production_order}.pdf"'

	return response
