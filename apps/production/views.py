from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.shortcuts import render, redirect
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.utils import timezone
from django.views import View
from django.views.decorators.http import require_POST
from django.views.generic import CreateView

from apps.info.models import Material, BoxSize, BoxType
from apps.production.forms import BoxModelForm, BoxOrderForm, BoxOrderDetailForm, BoxOrderDetailFormSet
from apps.production.models import BoxModel, Process, UploadImage, BoxOrder, BoxOrderDetail
from django.db.models import Q
import logging
from django.http import JsonResponse
from django.forms.models import inlineformset_factory


def base_html_view(request):
	return render(request, 'base.html')


class BoxModelListCreate(LoginRequiredMixin, View):
	def get(self, request):
		box_models = BoxModel.objects.all().order_by('-created_time')

		search_query = request.GET.get('search')
		if search_query:
			search_query = search_query.strip()
			box_models = box_models.filter(Q(name__icontains=search_query))

		page_size = request.GET.get("page_size", 12)
		paginator = Paginator(box_models, page_size)
		page_num = request.GET.get("page", 1)
		page_obj = paginator.get_page(page_num)
		context = {
			'box_models': page_obj,
			'form': BoxModelForm(),
			'materials': Material.objects.all(),
			'processes': Process.objects.all(),
			'box_sizes': BoxSize.objects.all(),
			'box_types': BoxType.objects.all(),
			'photos': UploadImage.objects.all(),
		}
		return render(request, "production/box_model_list.html", context)

	def post(self, request):
		form = BoxModelForm(request.POST)
		if form.is_valid():
			boxmodel = form.save(commit=False)
			boxmodel.created_by = request.user
			boxmodel.created_time = timezone.now()
			boxmodel.save()
			return redirect('box-model-list')
		context = {
			'boxmodels': BoxModel.objects.all().order_by('-created_time'),
			'form': form,
			'materials': Material.objects.all(),
			'processes': Process.objects.all(),
			'box_sizes': BoxSize.objects.all(),
			'box_types': BoxType.objects.all(),
			'photos': UploadImage.objects.all(),
		}
		return render(request, "production/box_model_list.html", context)


class BoxModelEdit(View, LoginRequiredMixin):
	def get(self, request, pk):
		boxmodel = get_object_or_404(BoxModel, pk=pk)
		form = BoxModelForm(instance=boxmodel)
		photos = UploadImage.objects.filter(box_model=boxmodel)
		context = {'form': form, 'boxmodel': boxmodel, 'photos': photos}
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


class BoxOrderListView(View):
	def get(self, request):
		queryset = BoxOrder.objects.all()

		search_query = request.GET.get('search')
		if search_query:
			search_query = search_query.strip()
			queryset = queryset.filter(Q(id__icontains=search_query))

		page_size = request.GET.get("page_size", 12)
		paginator = Paginator(queryset, page_size)
		page_num = request.GET.get("page", 1)
		page_obj = paginator.get_page(page_num)

		context = {
			'box_orders': page_obj,
		}
		return render(request, "production/box_order_list.html", context)


class BoxOrderListCreate(CreateView):
	model = BoxOrder
	form_class = BoxOrderForm
	template_name = 'production/box_order_create.html'
	success_url = reverse_lazy('box-order-list')

	def form_valid(self, form):
		order = form.save(commit=False)
		order.manager = self.request.user
		order.data = timezone.now()
		order.save()

		box_order_detail_formset = BoxOrderDetailFormSet(
			self.request.POST, instance=order
		)

		if box_order_detail_formset.is_valid():
			box_order_detail_formset.save(commit=False)
			for form in box_order_detail_formset.forms:
				if form.cleaned_data.get('box_model') and form.cleaned_data.get('amount'):
					box_order_detail = form.save(commit=False)
					box_order_detail.box_order = order
					box_order_detail.save()

		return super().form_valid(form)

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		if self.request.POST:
			context['order_detail_formset'] = BoxOrderDetailFormSet(
				self.request.POST, instance=self.object
			)
		else:
			context['order_detail_formset'] = BoxOrderDetailFormSet(
				instance=self.object
			)
		return context


@require_POST
def create_order_details(request):
	try:
		box_model_id = request.POST.get('boxorderdetail_set-0-box_model')
		amount = request.POST.get('boxorderdetail_set-0-amount')

		box_model = BoxModel.objects.get(id=box_model_id)

		box_order_detail = BoxOrderDetail.objects.create(box_model=box_model, amount=amount)

		return JsonResponse({'box_order_detail_id': box_order_detail.id})

	except Exception as e:
		return JsonResponse({'error': str(e)}, status=400)

#
# from django.contrib import messages
# from django.contrib.auth.mixins import LoginRequiredMixin
# from django.core.paginator import Paginator
# from django.shortcuts import render, redirect
# from django.shortcuts import get_object_or_404
# from django.urls import reverse_lazy
# from django.utils import timezone
# from django.views import View
# from django.views.decorators.http import require_POST
# from django.views.generic import CreateView
#
# from apps.info.models import Material, BoxSize, BoxType
# from apps.production.forms import BoxModelForm, BoxOrderForm, BoxOrderDetailForm, BoxOrderDetailFormSet
# from apps.production.models import BoxModel, Process, UploadImage, BoxOrder, BoxOrderDetail
# from django.db.models import Q
# from django.http import JsonResponse
# from django.forms.models import inlineformset_factory
#
#
# def base_html_view(request):
# 	return render(request, 'base.html')
#
#
# class BoxModelListCreate(LoginRequiredMixin, View):
# 	def get(self, request):
# 		box_models = BoxModel.objects.all().order_by('-created_time')
#
# 		search_query = request.GET.get('search')
# 		if search_query:
# 			search_query = search_query.strip()
# 			box_models = box_models.filter(Q(name__icontains=search_query))
#
# 		page_size = request.GET.get("page_size", 12)
# 		paginator = Paginator(box_models, page_size)
# 		page_num = request.GET.get("page", 1)
# 		page_obj = paginator.get_page(page_num)
# 		context = {
# 			'box_models': page_obj,
# 			'form': BoxModelForm(),
# 			'materials': Material.objects.all(),
# 			'processes': Process.objects.all(),
# 			'box_sizes': BoxSize.objects.all(),
# 			'box_types': BoxType.objects.all(),
# 			'photos': UploadImage.objects.all(),
# 		}
# 		return render(request, "production/box_model_list.html", context)
#
# 	def post(self, request):
# 		form = BoxModelForm(request.POST)
# 		if form.is_valid():
# 			boxmodel = form.save(commit=False)
# 			boxmodel.created_by = request.user
# 			boxmodel.created_time = timezone.now()
# 			boxmodel.save()
# 			return redirect('box-model-list')
# 		context = {
# 			'boxmodels': BoxModel.objects.all().order_by('-created_time'),
# 			'form': form,
# 			'materials': Material.objects.all(),
# 			'processes': Process.objects.all(),
# 			'box_sizes': BoxSize.objects.all(),
# 			'box_types': BoxType.objects.all(),
# 			'photos': UploadImage.objects.all(),
# 		}
# 		return render(request, "production/box_model_list.html", context)
#
#
# class BoxModelEdit(View, LoginRequiredMixin):
# 	def get(self, request, pk):
# 		boxmodel = get_object_or_404(BoxModel, pk=pk)
# 		form = BoxModelForm(instance=boxmodel)
# 		photos = UploadImage.objects.filter(box_model=boxmodel)
# 		context = {'form': form, 'boxmodel': boxmodel, 'photos': photos}
# 		return render(request, 'production/box_model_edit.html', context)
#
# 	def post(self, request, pk):
# 		boxmodel = get_object_or_404(BoxModel, pk=pk)
# 		form = BoxModelForm(request.POST, instance=boxmodel)
# 		if form.is_valid():
# 			form.save()
# 			messages.success(request, 'Changes saved successfully.')
# 			return redirect('production:box-model-list')
# 		else:
# 			messages.error(request, 'Please correct the errors below.')
# 		context = {'form': form, 'boxmodel': boxmodel}
# 		return render(request, 'production/box_model_edit.html', context)
#
#
# class BoxOrderListView(View):
# 	def get(self, request):
# 		queryset = BoxOrder.objects.all()
#
# 		search_query = request.GET.get('search')
# 		if search_query:
# 			search_query = search_query.strip()
# 			queryset = queryset.filter(Q(id__icontains=search_query))
#
# 		page_size = request.GET.get("page_size", 12)
# 		paginator = Paginator(queryset, page_size)
# 		page_num = request.GET.get("page", 1)
# 		page_obj = paginator.get_page(page_num)
#
# 		context = {
# 			'box_orders': page_obj,
# 		}
# 		return render(request, "production/box_order_list.html", context)
#
#
# class BoxOrderListCreate(CreateView):
# 	model = BoxOrder
# 	form_class = BoxOrderForm
# 	template_name = 'production/box_order_create.html'
# 	success_url = reverse_lazy('box-order-list')
#
# 	def form_valid(self, form):
# 		order = form.save(commit=False)
# 		order.manager = self.request.user
# 		order.data = timezone.now()
# 		order.save()
#
# 		BoxOrderDetailFormSet = inlineformset_factory(
# 			BoxOrder, BoxOrderDetail, form=BoxOrderDetailForm, extra=1
# 		)
# 		formset = BoxOrderDetailFormSet(
# 			self.request.POST, instance=order
# 		)
# 		if formset.is_valid():
# 			formset.save()
#
# 		return super().form_valid(form)
#
# 	def get_context_data(self, **kwargs):
# 		context = super().get_context_data(**kwargs)
# 		if self.request.POST:
# 			context['order_detail_formset'] = BoxOrderDetailFormSet(
# 				self.request.POST, instance=self.object
# 			)
# 		else:
# 			context['order_detail_formset'] = BoxOrderDetailFormSet(
# 				instance=self.object
# 			)
# 		return context
#
#
# @require_POST
# def create_order_details(request):
# 	try:
# 		box_model_id = request.POST.get('boxorderdetail_set-0-box_model')
# 		amount = request.POST.get('boxorderdetail_set-0-amount')
#
# 		box_model = BoxModel.objects.get(id=box_model_id)
#
# 		box_order_detail = BoxOrderDetail.objects.create(box_model=box_model, amount=amount)
#
# 		return JsonResponse({'box_order_detail_id': box_order_detail.id})
#
# 	except Exception as e:
# 		return JsonResponse({'error': str(e)}, status=400)
