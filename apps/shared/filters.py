import django_filters


class DatePeriodFilter(django_filters.FilterSet):
	created_time__gte = django_filters.DateTimeFilter(field_name='created_time', lookup_expr='gte',
													  label='Created Time (from)')
	created_time__lte = django_filters.DateTimeFilter(field_name='created_time', lookup_expr='lte',
													  label='Created Time (to')
