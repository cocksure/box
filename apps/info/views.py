from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import UpdateView

from apps.info.forms import MaterialTypeForm, WarehouseForm, MaterialForm, FirmForm, SpecificationForm, BoxSizesForm, \
	BoxTypesForm, MaterialSpecialGroupForm, BrandForm, MaterialGroupForm
from apps.info.models import MaterialType, Material, Warehouse, Firm, Specification, BoxSize, BoxType, \
	MaterialSpecialGroup, Brand, MaterialGroup
from apps.shared.views import BaseListCreateView


class MaterialTypeListCreate(BaseListCreateView):
	model = MaterialType
	form_class = MaterialTypeForm
	template_name = "info/material_type_list.html"
	redirect_url = "info:material_type-list"


class MaterialListCreate(BaseListCreateView):
	model = Material
	form_class = MaterialForm
	template_name = "info/material_list.html"
	redirect_url = "info:material-list"


class WarehouseListCreate(BaseListCreateView):
	model = Warehouse
	form_class = WarehouseForm
	template_name = "info/warehouse_list.html"
	redirect_url = "info:warehouse-list"


class FirmListCreate(BaseListCreateView):
	model = Firm
	form_class = FirmForm
	template_name = "info/firm_list.html"
	redirect_url = "info:firm-list"


class SpecificationListCreate(BaseListCreateView):
	model = Specification
	form_class = SpecificationForm
	template_name = "info/specification_list.html"
	redirect_url = "info:specification-list"


class BoxSizeListCreate(BaseListCreateView):
	model = BoxSize
	form_class = BoxSizesForm
	template_name = "info/box_size_list.html"
	redirect_url = "info:box_size-list"


class BoxTypeListCreate(BaseListCreateView):
	model = BoxType
	form_class = BoxTypesForm
	template_name = "info/box_type_list.html"
	redirect_url = "info:box_type-list"


class MaterialGroupListCreate(BaseListCreateView):
	model = MaterialGroup
	form_class = MaterialGroupForm
	template_name = "info/material_group_list.html"
	redirect_url = "info:material-group-list"


class MaterialSpecialGroupListCreate(BaseListCreateView):
	model = MaterialSpecialGroup
	form_class = MaterialSpecialGroupForm
	template_name = "info/material_special_group_list.html"
	redirect_url = "info:special-group-list"


class BrandListCreate(BaseListCreateView):
	model = Brand
	form_class = BrandForm
	template_name = "info/brand_list.html"
	redirect_url = "info:brand-list"


class MaterialEditView(View, LoginRequiredMixin):
	def get(self, request, pk):
		material = get_object_or_404(Material, pk=pk)
		form = MaterialForm(instance=material)
		context = {'form': form, 'material': material}
		return render(request, 'info/material_edit.html', context)

	def post(self, request, pk):
		material = get_object_or_404(Material, pk=pk)
		form = MaterialForm(request.POST, instance=material)
		if form.is_valid():
			form.save()
			return redirect('info:material-list')
		else:
			messages.error(request, 'Please correct the errors below.')
		context = {'form': form, 'material': material}
		return render(request, 'info/material_edit.html', context)


class FirmUpdateView(UpdateView):
	model = Firm
	form_class = FirmForm
	template_name = 'info/firm_update.html'
	success_url = reverse_lazy('info:firm-list')


class MaterialGroupUpdateView(UpdateView):
	model = MaterialGroup
	form_class = MaterialGroupForm
	template_name = 'info/material_group_update.html'
	success_url = reverse_lazy('info:material-group-list')
