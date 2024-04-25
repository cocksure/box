from collections import OrderedDict
from django.http import JsonResponse
from django.core.paginator import Paginator


class CustomPagination:
	page_size = 20
	max_page_size = 50

	def paginate_queryset(self, queryset, request, view=None):
		paginator = Paginator(queryset, self.page_size)
		page_number = request.query_params.get('page')
		paginated_queryset = paginator.get_page(page_number)
		return paginated_queryset

	def get_paginated_response(self, paginated_queryset):
		return JsonResponse(OrderedDict([
			('count', paginated_queryset.paginator.count),
			('current_page', paginated_queryset.number),
			('total_pages', paginated_queryset.paginator.num_pages),
			('next', paginated_queryset.next_page_number() if paginated_queryset.has_next() else None),
			('previous', paginated_queryset.previous_page_number() if paginated_queryset.has_previous() else None),
			('results', list(paginated_queryset))
		]))
