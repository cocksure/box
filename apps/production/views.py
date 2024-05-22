from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.utils import timezone
from django.views import View
from django.views.generic import CreateView, DetailView

from apps.depo.models.outgoing import Outgoing, OutgoingMaterial
from apps.depo.models.stock import Stock
from apps.info.models import Warehouse
from apps.production.forms import BoxModelForm, BoxOrderForm, BoxOrderDetailFormSet, BoxOrderDetailForm, \
	ProductionOrderForm
from apps.production.models import BoxModel, BoxOrder, BoxOrderDetail, ProductionOrder, TypeWork
from django.http import JsonResponse, HttpResponseRedirect
from django.db import transaction

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

		page_obj = self.apply_pagination_and_search(production_orders, request)

		context = {
			'items': page_obj,
			'production_orders': page_obj,
			'selected_status': status,
		}
		return render(request, "production/production_order_list.html", context)
