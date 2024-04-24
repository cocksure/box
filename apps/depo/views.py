from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.utils import timezone
from django.db import transaction
from django.http import JsonResponse, HttpResponseRedirect
from django.views.generic import DetailView, CreateView

from apps.depo.forms import IncomingForm, IncomingMaterialFormSet, OutgoingMaterialFormSet, OutgoingForm
from apps.depo.models.incoming import Incoming, IncomingMaterial
from apps.depo.models.outgoing import OutgoingMaterial, Outgoing
from apps.depo.models.stock import Stock
from apps.info.models import Material

from apps.shared.views import BaseListView


class IncomingListView(BaseListView):
	def get(self, request):
		incomings = Incoming.objects.all()
		page_obj = self.apply_pagination_and_search(incomings, request)

		context = {
			'incomings': page_obj,
		}

		return render(request, "depo/incoming_list.html", context)


class OutgoingListView(BaseListView):
	def get(self, request):
		outgoings = Outgoing.objects.all()
		page_obj = self.apply_pagination_and_search(outgoings, request)

		context = {
			'outgoings': page_obj,
		}

		return render(request, "depo/outgoing_list.html", context)


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
								outgoing=outgoing  # Используем сохраненный объект Outgoing
							)
							print("Material created:", material_id, amount, comment)
							outgoing_material_data.append({'material': material_id, 'amount': amount})

						except Material.DoesNotExist:
							print("Material with ID", material_id, "does not exist.")
						except Exception as e:
							print("Error while creating material:", e)

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
			return JsonResponse({'error': str(e)}, status=400)
		else:
			return HttpResponseRedirect(reverse_lazy('depo:outgoing-list'))

	def form_invalid(self, form):
		return JsonResponse({'success': False, 'errors': form.errors}, status=400)

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
