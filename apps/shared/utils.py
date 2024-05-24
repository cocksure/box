from collections import OrderedDict
from django.http import JsonResponse
from django.core.paginator import Paginator
import qrcode
from io import BytesIO


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


def generate_qr_code(data):
	if not data:
		return None

	qr = qrcode.QRCode(
		version=1,
		error_correction=qrcode.constants.ERROR_CORRECT_L,
		box_size=10,
		border=4,
	)
	qr.add_data(data)
	qr.make(fit=True)

	img = qr.make_image(fill_color="black", back_color="white")
	buffer = BytesIO()
	img.save(buffer, format="PNG")
	qr_code_data = buffer.getvalue()

	return qr_code_data
