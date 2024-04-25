from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View

from apps.shared.utils import CustomPagination
from django.core.paginator import Paginator
from django.db.models import Q


class BaseListView(LoginRequiredMixin, View):
	def apply_pagination_and_search(self, queryset, request):
		search_query = request.GET.get('search')
		if search_query:
			search_query = search_query.strip()
			queryset = queryset.filter(Q(name__icontains=search_query))

		page_size = request.GET.get("page_size", 12)
		paginator = Paginator(queryset, page_size)
		page_num = request.GET.get("page", 1)
		page_obj = paginator.get_page(page_num)
		return page_obj
