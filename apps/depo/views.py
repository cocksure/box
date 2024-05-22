from django.contrib import messages
from django.db.models import Q
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy, reverse
from django.utils import timezone
from django.db import transaction
from django.http import JsonResponse, HttpResponseRedirect, request
from django.views import View
from django.views.generic import DetailView, CreateView

from apps.depo.forms import IncomingForm, IncomingMaterialFormSet, OutgoingMaterialFormSet, OutgoingForm
from apps.depo.models.incoming import Incoming, IncomingMaterial
from apps.depo.models.outgoing import OutgoingMaterial, Outgoing
from apps.depo.models.stock import Stock
from apps.info.models import Material, Warehouse

from apps.shared.views import BaseListView


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

		if warehouse_id:
			queryset = queryset.filter(warehouse_id=warehouse_id)
			selected_warehouse_id = warehouse_id
		else:
			selected_warehouse_id = ""

		warehouses = Warehouse.objects.all()

		page_obj = self.apply_pagination_and_search(queryset, request)

		context = {
			'items': page_obj,
			'warehouses': warehouses,
			'selected_warehouse_id': selected_warehouse_id,

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
				print("Action:", action)

				outgoing.status = Outgoing.OutgoingStatus.REJECT
				outgoing.save()

			messages.success(request, "Успешно.")
		else:
			messages.error(request,
						   "Вы не являетесь менеджером склада и поэтому не можете принять или отклонить расход.")

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
							print("Material created:", material_id, amount, comment)
							incoming_material_data.append({'material': material_id, 'amount': amount})

						except Material.DoesNotExist:
							print("Material with ID", material_id, "does not exist.")
						except Exception as e:
							print("Error while creating material:", e)

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


		except Exception as e:
			return JsonResponse({'error': str(e)}, status=400)
		else:
			return HttpResponseRedirect(reverse_lazy('depo:incoming-list'))

	def form_invalid(self, form):
		return JsonResponse({'success': False, 'errors': form.errors}, status=400)

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

		# Проверяем наличие материалов на складе
		check_result, insufficient_materials = warehouse.has_enough_material(self.request.POST)

		if not check_result:
			error_message = 'Недостаточно материалов на складе'
			messages.error(self.request, error_message)

			# Сохраняем информацию о недостающих материалах в сессии
			self.request.session['insufficient_materials'] = insufficient_materials

			return super().form_invalid(form)

		try:
			with transaction.atomic():
				outgoing.save()

				detail_counter = int(self.request.POST.get('detail_counter', 0))
				outgoing_material_data = []

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
							print("Material with ID", material_id, "does not exist.")
						except Exception as e:
							print("Error while creating material:", e)

				# Проверяем, является ли тип исхода "Расход" или "Продажа",
				# и если да, то обновляем запасы на складе
				if outgoing.outgoing_type != Outgoing.OutgoingType.MOVEMENT:

					stocks_to_update = []
					warehouse = outgoing.warehouse

					for item in outgoing_material_data:
						material_id = item['material']
						amount = item['amount']

						material_instance = get_object_or_404(Material, id=material_id)

						amount = int(amount)
						stock, created = Stock.objects.get_or_create(material=material_instance, warehouse=warehouse)
						stock.amount -= amount  # Вычитаем количество из склада
						stocks_to_update.append(stock)

					Stock.objects.bulk_update(stocks_to_update, ['amount'])


		except Exception as e:
			messages.error(self.request, str(e))
			return super().form_invalid(form)
		else:
			return HttpResponseRedirect(reverse_lazy('depo:outgoing-list'))

	def form_invalid(self, form):
		# Добавляем сообщения об ошибках к форме
		for field, errors in form.errors.items():
			for error in errors:
				self.add_error(field, error)
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
