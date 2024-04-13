from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.db import transaction
from django.http import HttpResponseForbidden
from django.views import View
from django.views.generic import DetailView

from apps.depo.forms import IncomingForm, IncomingMaterialForm
from apps.depo.models.incoming import Incoming, IncomingMaterial
from apps.depo.models.stock import Stock
from apps.info.models import Warehouse, Material
from django.forms import modelformset_factory, inlineformset_factory

from apps.shared.views import BaseListView


class IncomingListView(View):
	def get(self, request):
		incomings = Incoming.objects.all().order_by('-created_time')

		search_query = request.GET.get('search')

		if search_query:
			search_query = search_query.strip()
			incomings = incomings.filter(Q(id__icontains=search_query))

		context = {'incomings': incomings, 'search_query': search_query}

		return render(request, 'depo/incoming_list.html', context)




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



class IncomingMaterialListCreate(BaseListView):
	def get(self, request):
		incoming_materials = IncomingMaterial.objects.all()

		context = {
			'incoming_materials': incoming_materials,
			'form': IncomingMaterialForm(),
		}
		return render(request, "depo/incoming_material_list_create.html", context)

	def post(self, request):
		form = IncomingMaterialForm(request.POST)
		if form.is_valid():
			incoming_material = form.save(commit=False)
			incoming_material.save()
			return redirect('depo:incoming-detail')
		context = {
			'incoming_materials': IncomingMaterial.objects.all(),
			'form': form,
		}
		return render(request, "depo/incoming_material_list_create.html", context)
