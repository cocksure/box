from django.views.generic import View
from django.shortcuts import render, redirect
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils import timezone


class BaseListView(View):
	@staticmethod
	def apply_pagination_and_search(queryset, request):
		search_query = request.GET.get('search')
		if search_query:
			search_query = search_query.strip()
			queryset = queryset.filter(Q(name__icontains=search_query))

		page_size = request.GET.get("page_size", 12)
		ordering = '-created_time'  # Specify the ordering here
		paginator = Paginator(queryset.order_by(ordering), page_size)
		page_num = request.GET.get("page", 1)
		page_obj = paginator.get_page(page_num)
		return page_obj

	@staticmethod
	def apply_pagination_and_search_by_code(queryset, request):
		search_query = request.GET.get('search')
		if search_query:
			search_query = search_query.strip()
			queryset = queryset.filter(
				Q(code__icontains=search_query)
			)

		page_size = request.GET.get("page_size", 12)
		paginator = Paginator(queryset, page_size)
		page_num = request.GET.get("page", 1)
		page_obj = paginator.get_page(page_num)
		return page_obj

	def get_queryset(self):
		return self.model.objects.all().order_by('-created_time')

	def get_form(self):
		return self.form_class

	def get_template_name(self):
		return self.template_name

	def get_redirect_url(self):
		return self.redirect_url

	def get_context_data(self, **kwargs):
		context = {}
		context.update(kwargs)
		return context

	def get(self, request):
		items = self.get_queryset()
		page_obj = self.apply_pagination_and_search(items, request)

		context = {
			'items': page_obj,
			'form': self.get_form(),
		}
		return render(request, self.get_template_name(), context)


class BaseListCreateView(BaseListView):
	def post(self, request):
		form = self.get_form()(request.POST, request.FILES)
		if form.is_valid():
			item = form.save(commit=False)
			item.created_by = request.user
			item.created_time = timezone.now()
			item.save()
			return redirect(self.get_redirect_url())
		context = {
			'items': self.get_queryset(),
			'form': form,
		}
		return render(request, self.get_template_name(), context)
