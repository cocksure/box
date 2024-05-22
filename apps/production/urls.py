from django.urls import path
from .views import BoxModelListCreate, BoxModelEditView, BoxOrderListView, BoxOrderCreate, BoxOrderDetailView, \
	ProductionOrderListView

app_name = 'production'

urlpatterns = [
	path('boxmodel/', BoxModelListCreate.as_view(), name='box-model-list'),
	path('boxmodel/edit/<int:pk>/', BoxModelEditView.as_view(), name='box-model-edit'),
	path('boxorders/', BoxOrderListView.as_view(), name='box-order-list'),
	path('productionorders/', ProductionOrderListView.as_view(), name='production-order-list'),
	path('boxorders/create/', BoxOrderCreate.as_view(), name='box-order-create'),
	path('box-order/<int:pk>/detail/', BoxOrderDetailView.as_view(), name='box-order-detail'),

]
