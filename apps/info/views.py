from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View

from apps.info.forms import MaterialTypeForm, WarehouseForm, MaterialForm, FirmForm, SpecificationForm, BoxSizesForm, \
	BoxTypesForm
from apps.info.models import MaterialType, Material, Warehouse, Firm, Specification, BoxSize, BoxType
from apps.shared.views import BaseListView


class MaterialTypeListCreate(BaseListView):
	def get(self, request):
		material_types = MaterialType.objects.all()
		page_obj = self.apply_pagination_and_search(material_types, request)

		context = {
			'material_types': page_obj,
			'form': MaterialTypeForm(),
		}
		return render(request, "info/material_type_list.html", context)

	def post(self, request):
		form = MaterialTypeForm(request.POST)
		if form.is_valid():
			material_type = form.save(commit=False)
			material_type.save()
			return redirect('info:material-type-list')
		context = {
			'material_types': MaterialType.objects.all(),
			'form': form,

		}
		return render(request, "info/material_type_list.html", context)


class MaterialListCreate(BaseListView):
	def get(self, request):
		materials = Material.objects.all().order_by('-created_time')
		page_obj = self.apply_pagination_and_search(materials, request)

		context = {
			'materials': page_obj,
			'form': MaterialForm(),
		}
		return render(request, "info/material_list.html", context)

	def post(self, request):
		form = MaterialForm(request.POST)
		if form.is_valid():
			material = form.save(commit=False)
			material.created_by = request.user
			material.created_time = timezone.now()
			material.save()
			return redirect('info:material-list')
		context = {
			'materials': Material.objects.all().order_by('-created_time'),
			'form': form,

		}
		return render(request, "info/material_list.html", context)


class WarehouseListCreate(BaseListView):
	def get(self, request):
		warehouses = Warehouse.objects.all().order_by('-created_time')
		page_obj = self.apply_pagination_and_search(warehouses, request)

		context = {
			'warehouses': page_obj,
			'form': WarehouseForm(),
		}
		return render(request, "info/warehouse_list.html", context)

	def post(self, request):
		form = WarehouseForm(request.POST)
		if form.is_valid():
			warehouse = form.save(commit=False)
			warehouse.created_by = request.user
			warehouse.created_time = timezone.now()
			warehouse.save()
			return redirect('info:warehouse-list')
		context = {
			'warehouses': Warehouse.objects.all().order_by('-created_time'),
			'form': form,
		}
		return render(request, "info/warehouse_list.html", context)


class FirmListCreate(BaseListView):
	def get(self, request):
		firms = Firm.objects.all().order_by('-created_time')
		page_obj = self.apply_pagination_and_search(firms, request)

		context = {
			'firms': page_obj,
			'form': FirmForm(),
		}
		return render(request, "info/firm_list.html", context)

	def post(self, request):
		form = FirmForm(request.POST)
		if form.is_valid():
			firm = form.save(commit=False)
			firm.created_by = request.user
			firm.created_time = timezone.now()
			firm.save()
			return redirect('info:firm-list')
		context = {
			'firms': Firm.objects.all().order_by('-created_time'),
			'form': form,

		}
		return render(request, "info/firm_list.html", context)


class SpecificationListCreate(BaseListView):
	def get(self, request):
		specifications = Specification.objects.all().order_by('-created_time')
		page_obj = self.apply_pagination_and_search(specifications, request)

		context = {
			'specifications': page_obj,
			'form': SpecificationForm(),
		}
		return render(request, "info/specification_list.html", context)

	def post(self, request):
		form = SpecificationForm(request.POST)
		if form.is_valid():
			specification = form.save(commit=False)
			specification.created_by = request.user
			specification.created_time = timezone.now()
			specification.save()
			return redirect('info:specification-list')
		context = {
			'specifications': Specification.objects.all().order_by('-created_time'),
			'form': form,

		}
		return render(request, "info/specification_list.html", context)


class BoxSizeListCreate(BaseListView):
	def get(self, request):
		box_sizes = BoxSize.objects.all()
		page_obj = self.apply_pagination_and_search(box_sizes, request)

		context = {
			'box_sizes': page_obj,
			'form': BoxSizesForm(),
		}
		return render(request, "info/box_size_list.html", context)

	def post(self, request):
		form = BoxSizesForm(request.POST)
		if form.is_valid():
			box_size = form.save(commit=False)
			box_size.save()
			return redirect('info:box_size-list')
		context = {
			'box_sizes': BoxSize.objects.all(),
			'form': form,

		}
		return render(request, "info/box_size_list.html", context)


class BoxTypeListCreate(BaseListView):
	def get(self, request):
		box_types = BoxType.objects.all()
		page_obj = self.apply_pagination_and_search(box_types, request)

		context = {
			'box_types': page_obj,
			'form': BoxTypesForm(),
		}
		return render(request, "info/box_type_list.html", context)

	def post(self, request):
		form = BoxTypesForm(request.POST)
		if form.is_valid():
			box_type = form.save(commit=False)
			box_type.save()
			return redirect('info:box_type-list')
		context = {
			'box_types': BoxSize.objects.all(),
			'form': form,
		}
		return render(request, "info/box_type_list.html", context)


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