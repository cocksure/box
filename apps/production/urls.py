from django.urls import path
from .views import BoxModelListCreate, BoxModelEditView, BoxOrderListView, BoxOrderCreate, BoxOrderDetailView, \
	ProductionOrderListView, process_log_view, ProcessLogListView, generate_box_order_pdf, \
	generate_production_order_pdf, packaging_view

app_name = 'production'

urlpatterns = [
	path('boxmodel/', BoxModelListCreate.as_view(), name='box-model-list'),
	path('boxmodel/edit/<int:pk>/', BoxModelEditView.as_view(), name='box-model-edit'),
	path('boxorders/', BoxOrderListView.as_view(), name='box-order-list'),
	path('productionorders/', ProductionOrderListView.as_view(), name='production-order-list'),
	path('boxorders/create/', BoxOrderCreate.as_view(), name='box-order-create'),
	path('box-order/<int:pk>/detail/', BoxOrderDetailView.as_view(), name='box-order-detail'),
	path('process-log/', process_log_view, name='process_log'),
	path('packaging/', packaging_view, name='packaging'),

	path('process-log-list/', ProcessLogListView.as_view(), name='process_log_list'),

	path('boxorder/<int:order_id>/pdf/', generate_box_order_pdf, name='generate_box_order_pdf'),
	path('productionorder/<int:production_order_id>/pdf/', generate_production_order_pdf,
		 name='generate_production_order_pdf'),

]
