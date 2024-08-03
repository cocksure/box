from decimal import Decimal, ROUND_HALF_UP

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

from apps.depo.models.incoming import Incoming, IncomingMaterial
from apps.depo.models.outgoing import Outgoing, OutgoingMaterial
from apps.depo.models.stock import Stock
from apps.info.models import Warehouse, Material, MaterialType, BoxSize
from apps.production.forms import BoxModelForm, BoxOrderForm, BoxOrderDetailFormSet, ProductionOrderForm, \
	ProcessLogForm, ProcessLogFilterForm, ProductionOrderCodeForm, PackagingAmountForm
from apps.production.models import BoxModel, BoxOrder, BoxOrderDetail, ProductionOrder, ProcessLog, Process
from django.http import JsonResponse, HttpResponseRedirect, HttpResponse
from django.db import transaction

from apps.production.utils import BoxProductionCalculation
from apps.shared.utils import generate_qr_code
from apps.shared.views import BaseListCreateView, BaseListView


class BoxModelListCreate(BaseListCreateView):
	model = BoxModel
	form_class = BoxModelForm
	template_name = "production/box_model_list.html"
	redirect_url = "production:box-model-list"


class BoxModelEditView(LoginRequiredMixin, View):
	def get(self, request, pk):
		boxmodel = get_object_or_404(BoxModel, pk=pk)
		form = BoxModelForm(instance=boxmodel)
		material_area = boxmodel.calculate_total_material_area()
		context = {
			'form': form,
			'boxmodel': boxmodel,
			'material_area': material_area,
		}
		return render(request, 'production/box_model_edit.html', context)

	def post(self, request, pk):
		boxmodel = get_object_or_404(BoxModel, pk=pk)
		form = BoxModelForm(request.POST, request.FILES, instance=boxmodel)
		if form.is_valid():
			form.save()
			messages.success(request, 'Изменения успешно сохранены.')
			return redirect('production:box-model-list')
		else:
			messages.error(request, 'Пожалуйста, исправьте ошибки ниже.')
		material_area = boxmodel.calculate_total_material_area()
		context = {
			'form': form,
			'boxmodel': boxmodel,
			'material_area': material_area,
		}
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
				messages.success(request, 'Статус заказа успешно обновлен.')
				return redirect('production:box-order-detail', pk=box_order.pk)
			else:
				messages.error(request, 'Неверный параметр статуса.')
				return redirect('production:box-order-detail', pk=box_order.pk)
		else:
			if box_order.status != BoxOrder.BoxOrderStatus.ACCEPT:
				messages.error(request, 'Производственный заказ можно создать только если заказ на коробки утвержден.')
				return redirect('production:box-order-detail', pk=box_order.pk)

			detail_id = request.POST.get('box_order_detail_id')
			try:
				detail = box_order.boxorderdetail_set.get(pk=detail_id)
			except BoxOrderDetail.DoesNotExist:
				messages.error(request, 'Неверный идентификатор детали заказа коробки.')
				return redirect('production:box-order-detail', pk=box_order.pk)

			# Проверка на существующий ProductionOrder для данного BoxOrderDetail
			if ProductionOrder.objects.filter(box_order_detail=detail).exists():
				messages.error(request, 'Производственный заказ для этой детали заказа коробки уже существует.')
				return redirect('production:box-order-detail', pk=box_order.pk)

			form = self.form_class(request.POST)
			if form.is_valid():
				grams_per_box = detail.box_model.grams_per_box
				if grams_per_box is None or detail.amount is None:
					messages.error(request, 'Грамм на одну коробку или количество не определен!')
					return redirect('production:box-order-detail', pk=box_order.pk)

				# Расчет общего количества материалов на основе "grams_per_box"
				total_material_amount = detail.amount * grams_per_box

				with transaction.atomic():
					production_order = form.save(commit=False)
					production_order.box_order_detail = detail
					production_order.amount = detail.amount
					production_order.created_by = request.user
					production_order.save()

					# Создаем запись о расходе
					warehouse_id = 3  # Расход из сурового склада
					try:
						warehouse = Warehouse.objects.get(pk=warehouse_id)
					except Warehouse.DoesNotExist:
						messages.error(request, 'Неверный идентификатор склада.')
						return redirect('production:box-order-detail', pk=box_order.pk)

					outgoing = Outgoing.objects.create(
						data=production_order.shipping_date,
						outgoing_type=Outgoing.OutgoingType.OUTGO,
						warehouse=warehouse,
						created_by=request.user
					)

					OutgoingMaterial.objects.create(
						outgoing=outgoing,
						material=detail.box_model.material,
						amount=total_material_amount,
						production_order=production_order  # Устанавливаем связь с ProductionOrder

					)

					# Обновляем запасы на складе
					stock, created = Stock.objects.get_or_create(material=detail.box_model.material,
																 warehouse=warehouse)
					if stock.amount < total_material_amount:
						transaction.set_rollback(True)
						messages.error(request, 'Недостаточно материалов на складе.')
						return redirect('production:box-order-detail', pk=box_order.pk)

					stock.amount -= total_material_amount
					stock.save()

				messages.success(request, 'Производственный заказ успешно создан.')
				return redirect('production:box-order-detail', pk=box_order.pk)
			else:
				messages.error(request, 'Ошибка проверки формы.')
				return redirect('production:box-order-detail', pk=box_order.pk)


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
			code_or_id = form.cleaned_data['production_order_code']
			try:
				if code_or_id.isdigit():
					production_order = ProductionOrder.objects.get(id=code_or_id)
				else:
					production_order = ProductionOrder.objects.get(code=code_or_id)

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
									 f'Процесс "{next_process.name}" отмечен как выполненный для заказа {production_order.code}.')

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
				messages.error(request, 'Заказ с таким кодом или ID не найден.')
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
		production_orders = set()

		for log in logs:
			production_order_id = log.production_order.id
			process_id = log.process.id

			production_orders.add(log.production_order)

			if production_order_id not in order_process_status:
				order_process_status[production_order_id] = {}
			order_process_status[production_order_id][process_id] = True

		page_obj = self.apply_pagination_and_search_by_code(logs, self.request)

		context.update({
			'form': self.form,
			'processes': processes,
			'items': page_obj,
			'order_process_status': order_process_status,
			'production_orders': list(production_orders)
		})
		return context

	def get(self, request, *args, **kwargs):
		context = self.get_context_data()
		return render(request, self.template_name, context)


def packaging_view(request):
	if request.method == 'POST':
		if 'production_order_code' in request.POST:
			code_form = ProductionOrderCodeForm(request.POST)
			if code_form.is_valid():
				code_or_id = code_form.cleaned_data['production_order_code']
				try:
					if code_or_id.isdigit():
						production_order = ProductionOrder.objects.get(id=code_or_id)
					else:
						production_order = ProductionOrder.objects.get(code=code_or_id)

					# Проверяем, завершены ли все процессы
					type_of_work = production_order.type_of_work
					processes = type_of_work.process.order_by('queue')
					completed_processes = ProcessLog.objects.filter(production_order=production_order).values_list(
						'process', flat=True
					)

					if not processes.exclude(id__in=completed_processes).exists():
						remaining_to_pack = production_order.amount - production_order.packed_amount
						request.session['production_order_id'] = str(production_order.id)
						request.session['remaining_to_pack'] = str(remaining_to_pack)
						messages.success(request, f'Можно упаковать до {remaining_to_pack} товаров!')
						return redirect('production:packaging')
					else:
						messages.error(request, 'Не все процессы завершены для этого заказа.')
				except ProductionOrder.DoesNotExist:
					messages.error(request, 'Заказ с таким кодом или ID не найден.')
		elif 'packed_amount' in request.POST:
			amount_form = PackagingAmountForm(request.POST)
			if amount_form.is_valid():
				packed_amount = amount_form.cleaned_data['packed_amount']
				production_order_id = request.session.get('production_order_id')
				remaining_to_pack = request.session.get('remaining_to_pack')

				if production_order_id and remaining_to_pack is not None:
					try:
						production_order = ProductionOrder.objects.get(id=production_order_id)
						remaining_to_pack = Decimal(remaining_to_pack)  # Преобразуем обратно в Decimal

						if packed_amount > remaining_to_pack:
							messages.error(request, f'Невозможно упаковать больше {remaining_to_pack} товаров.')
							return redirect('production:packaging')

						with transaction.atomic():
							production_order.packed_amount += packed_amount
							production_order.status = ProductionOrder.ProductionOrderStatus.PACKED
							production_order.save()

							warehouse_id = 4  # Приход на готовый склад
							try:
								warehouse = Warehouse.objects.get(pk=warehouse_id)
							except Warehouse.DoesNotExist:
								return JsonResponse({'error': 'Invalid warehouse ID'}, status=400)

							incoming = Incoming.objects.create(
								data=timezone.now(),
								warehouse=warehouse,
								created_by=request.user,
								created_time=timezone.now()
							)

							raw_material = production_order.box_order_detail.box_model.material
							finished_material_name = production_order.box_order_detail.box_model.name
							finished_material_type = get_object_or_404(MaterialType, name="Готовый продукт")

							finished_material, created = Material.objects.get_or_create(
								name=finished_material_name,
								defaults={
									'code': production_order.code,
									'material_group': raw_material.material_group,
									'special_group': raw_material.special_group,
									'brand': raw_material.brand,
									'material_type': finished_material_type,
									'material_thickness': raw_material.material_thickness,
									'unit_of_measurement': raw_material.unit_of_measurement
								}
							)

							IncomingMaterial.objects.create(
								material=finished_material,
								amount=packed_amount,
								comment='Упаковано',
								incoming=incoming
							)

							stock, created = Stock.objects.get_or_create(material=finished_material,
																		 warehouse=warehouse)
							stock.amount += packed_amount
							stock.save()

							messages.success(request, f'Упаковка завершена для заказа - {production_order.code}.')
							del request.session['production_order_id']
							del request.session['remaining_to_pack']
					except ProductionOrder.DoesNotExist:
						messages.error(request, 'Произошла ошибка, заказ не найден.')

					return redirect('production:packaging')
	else:
		code_form = ProductionOrderCodeForm()
		amount_form = PackagingAmountForm()

	return render(request, 'production/packaging.html', {
		'code_form': code_form,
		'amount_form': amount_form,
		'remaining_to_pack': request.session.get('remaining_to_pack')
	})


def calculate_box_production(request):
	context = {}

	if request.method == 'POST':
		material_id = request.POST.get('material')
		box_size_id = request.POST.get('box_size')
		layers = int(request.POST.get('layers', 1))
		quantity = request.POST.get('quantity', 1)  # Обязательно извлеките значение quantity
		norm_starch = Decimal(request.POST.get('norm_starch', '0.025'))
		norm_glue = Decimal(request.POST.get('norm_glue', '0.025'))
		norm_paint = Decimal(request.POST.get('norm_paint', '0.025'))

		quantity = int(quantity) if quantity else 1

		material = get_object_or_404(Material, id=material_id)
		box_size = get_object_or_404(BoxSize, id=box_size_id)

		calculator = BoxProductionCalculation(
			material, box_size, layers, quantity, norm_starch, norm_glue, norm_paint
		)

		# Calculate results
		single_box_area = calculator.calculate_single_box_area().quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
		total_area = calculator.calculate_total_area().quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
		single_starch_consumption, total_starch_consumption = map(
			lambda x: x.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP),
			calculator.calculate_starch_consumption()
		)
		single_glue_consumption, total_glue_consumption = map(
			lambda x: x.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP),
			calculator.calculate_glue_consumption()
		)
		single_paint_consumption, total_paint_consumption = map(
			lambda x: x.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP),
			calculator.calculate_paint_consumption()
		)
		single_material_consumption, total_material_consumption = map(
			lambda x: x.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP),
			calculator.material_consumption()
		)

		# Populate context with results
		context.update({
			'single_box_area': single_box_area,
			'total_area': total_area,
			'single_starch_consumption': single_starch_consumption,
			'total_starch_consumption': total_starch_consumption,
			'single_glue_consumption': single_glue_consumption,
			'total_glue_consumption': total_glue_consumption,
			'single_paint_consumption': single_paint_consumption,
			'total_paint_consumption': total_paint_consumption,
			'single_material_consumption': single_material_consumption,
			'total_material_consumption': total_material_consumption,
			'quantity': quantity  # Добавляем quantity в контекст
		})

	# Fetch all materials and box sizes for the form
	materials = Material.objects.all()
	box_sizes = BoxSize.objects.all()

	context.update({
		'materials': materials,
		'box_sizes': box_sizes
	})

	return render(request, 'production/calculate_box_production.html', context)


# ----------------------------------------PDF views start----------------------------------------------------------
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
	box_order_detail = production_order.box_order_detail
	box_order = box_order_detail.box_order
	box_model = box_order_detail.box_model

	# Генерация QR-кода (если требуется)
	qr_code_data = generate_qr_code(production_order.code)

	# Получение процессов, связанных с типом работы
	processes = Process.objects.all()

	# Создание словаря для хранения информации о процессах для всех заказов на производство
	all_production_orders = ProductionOrder.objects.all()
	order_process_status = {}

	for order in all_production_orders:
		order_process_status[order.id] = {}
		logs = ProcessLog.objects.filter(production_order=order)
		for log in logs:
			process_id = log.process.id
			order_process_status[order.id][process_id] = True

	photo_url = request.build_absolute_uri(box_model.photo.url)

	context = {
		'order': production_order,
		'qr_code_data': qr_code_data,
		'box_order': box_order,
		'box_model': box_model,
		'photo_url': photo_url,
		'order_details': box_order_detail,
		'processes': processes,
		'order_process_status': order_process_status,
		'production_orders': all_production_orders,
	}

	html_string = render_to_string('pdf/production_order_pdf.html', context)
	html = HTML(string=html_string, base_url=request.build_absolute_uri('/'))
	pdf = html.write_pdf()

	response = HttpResponse(pdf, content_type='application/pdf')
	response['Content-Disposition'] = f'attachment; filename="production_order_{production_order.id}.pdf"'

	return response

# ----------------------------------------PDF views finish----------------------------------------------------------
