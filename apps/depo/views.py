from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy, reverse
from django.utils import timezone
from django.db import transaction
from django.http import JsonResponse, HttpResponseRedirect, HttpResponse
from django.views import View
from django.views.generic import DetailView, CreateView

from apps.depo.forms import IncomingForm, IncomingMaterialFormSet, OutgoingMaterialFormSet, OutgoingForm, SaleForm, \
	MaterialCodeForm
from apps.depo.models.incoming import Incoming, IncomingMaterial
from apps.depo.models.outgoing import OutgoingMaterial, Outgoing
from apps.depo.models.stock import Stock
from apps.info.models import Material, Warehouse, MaterialType, Firm

from apps.shared.views import BaseListView
from django.contrib import messages
from django.template.loader import render_to_string
from weasyprint import HTML


class IncomingListView(BaseListView):
	model = Incoming
	form_class = None
	template_name = "depo/incoming_list.html"
	redirect_url = "depo:incoming-list"


class OutgoingListView(BaseListView):
	model = Outgoing
	form_class = None
	template_name = "depo/outgoing_list.html"
	redirect_url = "depo:outgoing-list"


class StockListView(BaseListView):
	template_name = "depo/stock_list.html"

	def get(self, request):
		queryset = Stock.objects.all()
		warehouse_id = request.GET.get('warehouse_id')
		material_type_id = request.GET.get('material_type')
		format_id = request.GET.get('format')
		customer_id = request.GET.get('customer_id')

		if warehouse_id:
			queryset = queryset.filter(warehouse_id=warehouse_id)
			selected_warehouse_id = warehouse_id
		else:
			selected_warehouse_id = ""

		if material_type_id:
			queryset = queryset.filter(material__material_type=material_type_id)
			selected_material_type_id = material_type_id
		else:
			selected_material_type_id = ""

		if format_id:
			queryset = queryset.filter(material__format=format_id)
			selected_format_id = format_id
		else:
			selected_format_id = ""

		if customer_id:
			queryset = queryset.filter(material__customer_id=customer_id)
			selected_customer_id = customer_id
		else:
			selected_customer_id = ""

		warehouses = Warehouse.objects.all()
		material_types = MaterialType.objects.all()
		formats = dict(Material.FORMAT_CHOICES)
		customers = Firm.objects.all()

		page_obj = self.apply_pagination_and_search(queryset, request)

		context = {
			'items': page_obj,
			'warehouses': warehouses,
			'material_types': material_types,
			'formats': formats,
			'customers': customers,
			'selected_warehouse_id': selected_warehouse_id,
			'selected_material_type_id': selected_material_type_id,
			'selected_format_id': selected_format_id,
			'selected_customer_id': selected_customer_id,

		}
		return render(request, self.template_name, context)


class UnacceptedOutgoingsView(BaseListView):
	model = Outgoing
	form_class = None
	template_name = "depo/outgoing_list.html"
	redirect_url = "depo:unaccepted-list"

	def get_queryset(self):
		return self.model.objects.filter(status=Outgoing.OutgoingStatus.IN_PROGRESS).order_by('-created_time')


class OutgoingDetailView(View):
	template_name = 'depo/outgoing_detail.html'

	def get(self, request, *args, **kwargs):
		outgoing_id = kwargs.get('pk')
		try:
			outgoing = Outgoing.objects.get(pk=outgoing_id)
			outgoing_materials = OutgoingMaterial.objects.filter(outgoing=outgoing)
			context = {
				'outgoing': outgoing,
				'outgoing_materials': outgoing_materials,
			}
			return render(request, self.template_name, context)
		except Outgoing.DoesNotExist:
			return render(request, self.template_name, {'error_message': 'Outgoing object does not exist'})

	def post(self, request, *args, **kwargs):

		outgoing_id = kwargs.get('pk')
		outgoing = get_object_or_404(Outgoing, pk=outgoing_id)
		action = request.POST.get('action')

		# Проверка прав доступа
		warehouse = outgoing.to_warehouse
		managers = warehouse.managers.all()

		if request.user.is_authenticated and request.user in managers:

			if action == 'accept':
				# Обработка принятия расхода
				outgoing.status = Outgoing.OutgoingStatus.ACCEPT
				outgoing.save()

				# Если это перемещение, создаем автоматический приход на склад-получатель
				if outgoing.outgoing_type == Outgoing.OutgoingType.MOVEMENT:
					with transaction.atomic():
						incoming = Incoming.objects.create(
							data=outgoing.data,
							outgoing=outgoing,
							warehouse=outgoing.to_warehouse,
							from_warehouse=outgoing.warehouse,
							incoming_type=Incoming.MOVEMENT,
							created_by=request.user,
							created_time=timezone.now()
						)
						for material_item in outgoing.outgoing_materials.all():
							IncomingMaterial.objects.create(
								incoming=incoming,
								material=material_item.material,
								amount=material_item.amount,
								material_party=material_item.material_party,
								comment=material_item.comment
							)

				# Логируем информацию о присваивании значения outgoing
				stocks_to_update = []
				warehouse = outgoing.warehouse
				to_warehouse = outgoing.to_warehouse
				for material_item in outgoing.outgoing_materials.all():
					material_instance = material_item.material
					amount = material_item.amount

					# Уменьшаем количество материала на складе-отправителе
					stock, created = Stock.objects.get_or_create(material=material_instance, warehouse=warehouse)
					stock.amount -= amount
					stocks_to_update.append(stock)

					# Увеличиваем количество материала на складе-получателе
					to_stock, created = Stock.objects.get_or_create(material=material_instance, warehouse=to_warehouse)
					to_stock.amount += amount
					to_stock.save()

				# Обновляем записи остатков на обоих складах
				Stock.objects.bulk_update(stocks_to_update, ['amount'])

			elif action == 'reject':

				outgoing.status = Outgoing.OutgoingStatus.REJECT
				outgoing.save()

			messages.success(request, "Успешно.")
		else:
			messages.error(request, "Вы не являетесь менеджером этого склада .")

		# Возвращаем пользователя на страницу деталей этого Outgoing объекта после изменения его статуса
		return HttpResponseRedirect(reverse('depo:outgoing-detail', kwargs={'pk': outgoing_id}))


class IncomingDetailView(DetailView):
	model = Incoming
	template_name = 'depo/incoming_detail.html'
	context_object_name = 'incoming'

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		incoming = self.object
		incoming_materials = incoming.incomingmaterial_set.all()
		context['incoming_materials'] = incoming_materials
		return context


class IncomingCreate(CreateView):
	model = Incoming
	form_class = IncomingForm
	template_name = 'depo/incoming_create.html'

	def form_valid(self, form):
		incoming = form.save(commit=False)
		incoming.data = timezone.now()
		incoming.created_by = self.request.user
		incoming.created_time = timezone.now()

		try:
			with transaction.atomic():
				incoming.save()

				detail_counter = int(self.request.POST.get('detail_counter', 0))
				incoming_material_data = []

				for detail_index in range(1, detail_counter + 1):
					material_id = self.request.POST.get('incoming_material_' + str(detail_index))
					amount = self.request.POST.get('incoming_amount_' + str(detail_index))
					comment = self.request.POST.get('incoming_comment_' + str(detail_index))

					if material_id and amount:
						try:
							material = Material.objects.get(id=material_id)
							IncomingMaterial.objects.create(
								material=material,
								amount=amount,
								comment=comment,
								incoming=incoming
							)
							incoming_material_data.append({'material': material_id, 'amount': amount})
						except Material.DoesNotExist:
							messages.error(self.request, f"Материал с ID {material_id} не существует.")
						except Exception as e:
							messages.error(self.request, f"Ошибка при создании материала: {e}")

				stocks_to_update = []
				warehouse = incoming.warehouse

				for item in incoming_material_data:
					material_id = item['material']
					amount = item['amount']

					material_instance = get_object_or_404(Material, id=material_id)

					amount = int(amount)
					stock, created = Stock.objects.get_or_create(material=material_instance, warehouse=warehouse)
					stock.amount += amount
					stocks_to_update.append(stock)

				Stock.objects.bulk_update(stocks_to_update, ['amount'])

		# messages.success(self.request, "Приход Успешно создан!")

		except Exception as e:
			messages.error(self.request, f"Error: {e}")
			return JsonResponse({'error': str(e)}, status=400)
		else:
			return HttpResponseRedirect(reverse_lazy('depo:incoming-list'))

	def form_invalid(self, form):
		for field, errors in form.errors.items():
			for error in errors:
				messages.error(self.request, f"{field}: {error}")
		return super().form_invalid(form)

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		if self.object:
			context['material_formset'] = IncomingMaterialFormSet(
				self.request.POST if self.request.method == 'POST' else None,
				instance=self.object
			)
		else:
			context['material_formset'] = IncomingMaterialFormSet()
		return context


class OutgoingCreate(CreateView):
	model = Outgoing
	form_class = OutgoingForm
	template_name = 'depo/outgoing_create.html'

	def form_valid(self, form):
		outgoing = form.save(commit=False)
		outgoing.date = timezone.now()
		outgoing.created_by = self.request.user
		outgoing.created_time = timezone.now()

		warehouse_id = self.request.POST.get('warehouse')
		warehouse = get_object_or_404(Warehouse, id=warehouse_id)

		check_result, insufficient_materials = self.check_material_availability(warehouse)

		if not check_result:
			error_message = 'Недостаточно материалов на складе'
			messages.error(self.request, error_message)
			self.request.session['insufficient_materials'] = insufficient_materials
			return super().form_invalid(form)

		try:
			with transaction.atomic():
				outgoing.save()
				outgoing_material_data = self.save_outgoing_materials(outgoing)

				if outgoing.outgoing_type != Outgoing.OutgoingType.MOVEMENT:
					self.update_stock(outgoing, outgoing_material_data)

		except Exception as e:
			messages.error(self.request, str(e))
			return super().form_invalid(form)

		messages.success(self.request, "Запись о исходящем материале успешно создана.")
		return HttpResponseRedirect(reverse_lazy('depo:outgoing-list'))

	def form_invalid(self, form):
		for field, errors in form.errors.items():
			for error in errors:
				messages.error(self.request, f"{field}: {error}")
		return super().form_invalid(form)

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		if self.object:
			context['material_formset'] = OutgoingMaterialFormSet(
				self.request.POST if self.request.method == 'POST' else None,
				instance=self.object
			)
		else:
			context['material_formset'] = OutgoingMaterialFormSet()
		return context

	def check_material_availability(self, warehouse):
		return warehouse.has_enough_material(self.request.POST)

	def save_outgoing_materials(self, outgoing):
		outgoing_material_data = []
		detail_counter = int(self.request.POST.get('detail_counter', 0))

		for detail_index in range(1, detail_counter + 1):
			material_id = self.request.POST.get('outgoing_material_' + str(detail_index))
			amount = self.request.POST.get('outgoing_amount_' + str(detail_index))
			comment = self.request.POST.get('outgoing_comment_' + str(detail_index))

			if material_id and amount:
				try:
					material = Material.objects.get(id=material_id)
					OutgoingMaterial.objects.create(
						material=material,
						amount=amount,
						comment=comment,
						outgoing=outgoing
					)
					outgoing_material_data.append({'material': material_id, 'amount': amount})
				except Material.DoesNotExist:
					messages.error(self.request, f"Материал с ID {material_id} не существует.")
				except Exception as e:
					messages.error(self.request, f"Ошибка при создании материала: {e}")
		return outgoing_material_data

	def update_stock(self, outgoing, outgoing_material_data):
		stocks_to_update = []
		warehouse = outgoing.warehouse

		for item in outgoing_material_data:
			material_id = item['material']
			amount = item['amount']

			material_instance = get_object_or_404(Material, id=material_id)

			amount = int(amount)
			stock, created = Stock.objects.get_or_create(material=material_instance, warehouse=warehouse)
			stock.amount -= amount
			stocks_to_update.append(stock)

		Stock.objects.bulk_update(stocks_to_update, ['amount'])


def sale_create_view(request):
	code_form = MaterialCodeForm()
	amount_form = SaleForm()
	remaining_to_pack = None
	material_info = None

	if request.method == 'POST':
		if 'check_code' in request.POST:
			code_form = MaterialCodeForm(request.POST)
			if code_form.is_valid():
				material_code = code_form.cleaned_data['material_code']
				try:
					material = Material.objects.get(code=material_code, material_type_id=2)
					stock = Stock.objects.get(material=material)
					remaining_to_pack = stock.amount
					material_info = {
						'name': material.name,
						'available_amount': stock.amount,
					}
				except Material.DoesNotExist:
					messages.error(request, 'Материал не найден или не подходит.')
				except Stock.DoesNotExist:
					messages.error(request, 'Материал отсутствует на складе.')

				return render(request, 'depo/sale_create.html', {
					'code_form': code_form,
					'amount_form': amount_form,
					'remaining_to_pack': remaining_to_pack,
					'material_info': material_info
				})
		elif 'submit_sale' in request.POST:
			amount_form = SaleForm(request.POST)
			if amount_form.is_valid():
				quantity = amount_form.cleaned_data['quantity']
				material_code = request.POST.get('material_code')

				try:
					material = Material.objects.get(code=material_code, material_type_id=2)
					stock = Stock.objects.get(material=material)

					if stock.amount < quantity:
						messages.error(request, 'Недостаточно материалов на складе.')
						return redirect('depo:sale-create')

					# Create outgoing record
					with transaction.atomic():
						outgoing = Outgoing.objects.create(
							data=timezone.now(),
							outgoing_type=Outgoing.OutgoingType.SALE,
							warehouse=stock.warehouse,
							created_by=request.user
						)

						OutgoingMaterial.objects.create(
							outgoing=outgoing,
							material=material,
							amount=quantity
						)

						# Update stock
						stock.amount -= quantity
						stock.save()

						messages.success(request, 'Продажа успешно оформлена.')
						return redirect('depo:outgoing-list')  # Redirect to a success page or another view
				except (Material.DoesNotExist, Stock.DoesNotExist):
					messages.error(request, 'Ошибка при обработке продажи.')
			else:
				messages.error(request, 'Пожалуйста, исправьте ошибки в форме.')

	return render(request, 'depo/sale_create.html', {
		'code_form': code_form,
		'amount_form': amount_form,
		'remaining_to_pack': remaining_to_pack,
		'material_info': material_info
	})


class IncomingPDFView(View):
	def get(self, request, *args, **kwargs):
		incoming = get_object_or_404(Incoming, pk=kwargs['pk'])
		incoming_materials = incoming.incomingmaterial_set.all()

		# Подготовка контекста для шаблона
		context = {
			'incoming': incoming,
			'incoming_materials': incoming_materials,
		}

		# Рендеринг HTML-шаблона в строку
		html_string = render_to_string('pdf/incoming_detail_pdf.html', context)

		# Генерация PDF из HTML-строки
		html = HTML(string=html_string)
		pdf_file = html.write_pdf()

		# Возвращение PDF-файла как ответа
		response = HttpResponse(pdf_file, content_type='application/pdf')
		response['Content-Disposition'] = f'inline; filename="incoming_{incoming.id}.pdf"'

		return response


class OutgoingPDFView(View):
	def get(self, request, *args, **kwargs):
		outgoing = get_object_or_404(Outgoing, pk=kwargs['pk'])
		outgoing_materials = outgoing.outgoing_materials.all()

		# Подготовка контекста для шаблона
		context = {
			'outgoing': outgoing,
			'outgoing_materials': outgoing_materials,
		}

		# Рендеринг HTML-шаблона в строку
		html_string = render_to_string('pdf/outgoing_detail_pdf.html', context)

		# Генерация PDF из HTML-строки
		html = HTML(string=html_string)
		pdf_file = html.write_pdf()

		# Возвращение PDF-файла как ответа
		response = HttpResponse(pdf_file, content_type='application/pdf')
		response['Content-Disposition'] = f'inline; filename="incoming_{outgoing.id}.pdf"'

		return response
